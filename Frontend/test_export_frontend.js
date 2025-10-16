/**
 * Frontend Export Test Script
 * Run this in the browser console when logged in as SuperAdmin
 */

// Test 1: Basic export test
async function testBasicExport() {
  console.log('🧪 Testing basic export...');
  
  try {
    const response = await fetch('/api/survey/admin/export/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
      },
      body: JSON.stringify({
        format: 'xlsx',
        category_id: null,
        date_from: null,
        date_to: null
      })
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', [...response.headers.entries()]);
    
    if (response.ok) {
      const blob = await response.blob();
      console.log('✅ Export successful - Blob size:', blob.size, 'bytes');
      
      // Test download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'test_export.xlsx';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return { success: true, size: blob.size };
    } else {
      const errorText = await response.text();
      console.error('❌ Export failed:', response.status, errorText);
      return { success: false, error: errorText, status: response.status };
    }
  } catch (error) {
    console.error('❌ Export error:', error);
    return { success: false, error: error.message };
  }
}

// Test 2: Category-specific export
async function testCategoryExport(categoryId = 1) {
  console.log(`🧪 Testing category ${categoryId} export...`);
  
  try {
    const response = await fetch('/api/survey/admin/export/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
      },
      body: JSON.stringify({
        format: 'xlsx',
        category_id: categoryId,
        date_from: null,
        date_to: null
      })
    });
    
    console.log('Response status:', response.status);
    
    if (response.ok) {
      const blob = await response.blob();
      console.log(`✅ Category ${categoryId} export successful - Blob size:`, blob.size, 'bytes');
      return { success: true, size: blob.size };
    } else {
      const errorText = await response.text();
      console.error(`❌ Category ${categoryId} export failed:`, response.status, errorText);
      return { success: false, error: errorText, status: response.status };
    }
  } catch (error) {
    console.error(`❌ Category ${categoryId} export error:`, error);
    return { success: false, error: error.message };
  }
}

// Test 3: Check available categories
async function getAvailableCategories() {
  console.log('🧪 Getting available categories...');
  
  try {
    const response = await fetch('/api/survey/admin/categories/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const categories = await response.json();
      console.log('📋 Available categories:', categories);
      return categories;
    } else {
      console.error('❌ Failed to get categories');
      return [];
    }
  } catch (error) {
    console.error('❌ Error getting categories:', error);
    return [];
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting frontend export tests...');
  
  // Get categories first
  const categories = await getAvailableCategories();
  
  // Test basic export
  const basicResult = await testBasicExport();
  
  // Test category exports if categories exist
  const categoryResults = [];
  if (categories.length > 0) {
    for (const category of categories.slice(0, 3)) { // Test first 3 categories
      const result = await testCategoryExport(category.id);
      categoryResults.push({ category: category.name, ...result });
    }
  }
  
  // Summary
  console.log('📊 Test Results Summary:');
  console.log('Basic Export:', basicResult);
  console.log('Category Exports:', categoryResults);
  
  return {
    basic: basicResult,
    categories: categoryResults,
    totalCategories: categories.length
  };
}

// Instructions
console.log(`
🎯 Frontend Export Test Script Loaded!

To run tests, execute in browser console:
1. runAllTests() - Run complete test suite
2. testBasicExport() - Test basic all-data export  
3. testCategoryExport(1) - Test specific category export
4. getAvailableCategories() - Check available categories

Make sure you're logged in as SuperAdmin first!
`);

// Export functions to global scope
window.testBasicExport = testBasicExport;
window.testCategoryExport = testCategoryExport;
window.getAvailableCategories = getAvailableCategories;
window.runAllTests = runAllTests;