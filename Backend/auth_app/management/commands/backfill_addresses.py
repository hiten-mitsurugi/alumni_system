"""
Management command to backfill Address model from existing CustomUser address fields.
This is a safe, idempotent operation that creates Address rows without modifying existing data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from auth_app.models import CustomUser, Address
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def normalize_text(s):
    """Normalize text for deduplication comparison"""
    if not s:
        return ''
    return ' '.join(s.strip().lower().split())


class Command(BaseCommand):
    help = "Backfill Address model from CustomUser address fields"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=BATCH_SIZE,
            help=f'Number of users to process in each batch (default: {BATCH_SIZE})',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get total count
        total_users = CustomUser.objects.count()
        self.stdout.write(f"Processing {total_users} users in batches of {batch_size}")

        created_count = 0
        reused_count = 0
        processed_count = 0
        error_count = 0

        # Process users in batches
        for offset in range(0, total_users, batch_size):
            users_batch = CustomUser.objects.all().order_by('id')[offset:offset + batch_size]
            
            for user in users_batch:
                try:
                    with transaction.atomic():
                        # Process present address
                        present_created, present_reused = self._process_address(
                            user, 'present', dry_run
                        )
                        
                        # Process permanent address
                        permanent_created, permanent_reused = self._process_address(
                            user, 'permanent', dry_run
                        )
                        
                        created_count += present_created + permanent_created
                        reused_count += present_reused + permanent_reused
                        
                except Exception as e:
                    logger.error(f"Error processing user {user.id} ({user.email}): {str(e)}")
                    error_count += 1
                    
                processed_count += 1
                
            # Progress update
            self.stdout.write(
                f"Processed {min(offset + batch_size, total_users)}/{total_users} users. "
                f"Created: {created_count}, Reused: {reused_count}, Errors: {error_count}"
            )

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nBackfill complete!\n"
                f"Processed: {processed_count} users\n"
                f"Created: {created_count} addresses\n"
                f"Reused: {reused_count} addresses\n"
                f"Errors: {error_count}"
            )
        )

    def _process_address(self, user, category, dry_run=False):
        """Process a single address category for a user"""
        created = 0
        reused = 0
        
        # Skip if Address already exists for this user/category
        if Address.objects.filter(user=user, address_category=category).exists():
            logger.info(f"Address already exists for user {user.id} - {category}")
            return created, reused

        # Get address data from CustomUser fields
        address_data = self._extract_address_data(user, category)
        
        if not address_data:
            logger.info(f"No address data found for user {user.id} - {category}")
            return created, reused

        # Generate normalized text for deduplication
        normalized_text = self._generate_normalized_text(address_data)
        
        if not normalized_text:
            logger.info(f"Empty normalized text for user {user.id} - {category}")
            return created, reused

        # Try to find existing Address with same normalized text
        existing_address = Address.objects.filter(
            normalized_text=normalized_text,
            address_type=address_data['address_type']
        ).first()

        if existing_address:
            # Reuse existing address if user doesn't already have one for this category
            if not dry_run:
                # Create new Address row linking to same user but different category
                # (We can't reuse across users due to unique_together constraint)
                Address.objects.create(
                    user=user,
                    address_category=category,
                    **address_data
                )
            reused = 1
            logger.info(f"Reused address pattern for user {user.id} - {category}")
        else:
            # Create new address
            if not dry_run:
                Address.objects.create(
                    user=user,
                    address_category=category,
                    **address_data
                )
            created = 1
            logger.info(f"Created new address for user {user.id} - {category}")

        return created, reused

    def _extract_address_data(self, user, category):
        """Extract address data from CustomUser fields"""
        prefix = f"{category}_"
        
        # Get address type
        address_type = getattr(user, f"{prefix}address_type", None) or 'philippines'
        
        # Extract structured fields
        data = {
            'address_type': address_type,
            'region_code': getattr(user, f"{prefix}region_code", None) or '',
            'region_name': getattr(user, f"{prefix}region_name", None) or '',
            'province_code': getattr(user, f"{prefix}province_code", None) or '',
            'province_name': getattr(user, f"{prefix}province_name", None) or '',
            'city_code': getattr(user, f"{prefix}city_code", None) or '',
            'city_name': getattr(user, f"{prefix}city_name", None) or '',
            'barangay': getattr(user, f"{prefix}barangay", None) or '',
            'street_address': getattr(user, f"{prefix}street_address", None) or '',
            'postal_code': getattr(user, f"{prefix}postal_code", None) or '',
            'country': getattr(user, f"{prefix}country", None) or '',
            'full_address': getattr(user, f"{prefix}full_address", None) or '',
        }
        
        # Fallback to legacy text field if no structured data
        legacy_field = getattr(user, f"{prefix}address", None)
        if not any(data.values()) and legacy_field:
            data.update({
                'address_type': 'international',  # Assume international for legacy text
                'full_address': legacy_field,
                'country': 'Unknown',
            })
        
        # Only return data if we have something meaningful
        if any(v for v in data.values() if v):
            return data
        
        return None

    def _generate_normalized_text(self, address_data):
        """Generate normalized text from address data for comparison"""
        if address_data['address_type'] == 'philippines':
            parts = []
            for field in ['street_address', 'barangay', 'city_name', 'province_name', 'region_name', 'postal_code']:
                if address_data.get(field):
                    if field == 'barangay':
                        parts.append(f"Brgy. {address_data[field]}")
                    else:
                        parts.append(address_data[field])
            return normalize_text(", ".join(parts)) if parts else ''
        else:
            # International
            if address_data.get('full_address') and address_data.get('country'):
                return normalize_text(f"{address_data['full_address']}, {address_data['country']}")
            return normalize_text(address_data.get('full_address', ''))