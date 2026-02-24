# Message Edit & Delete Functionality Fix

## Problem
Messages were not being deleted or edited in real-time for all participants:
- **Sender**: Could see updates immediately (after refresh or reconnect)
- **Receiver**: Could NOT see updates in real-time - needed to refresh the page

## Root Causes

### 1. Event Data Structure Mismatch (SOLVED)
**File**: `Frontend/src/composables/useMessageActions.js`
- **Issue**: The `handleMessageAction` function expected separate parameters `(action, message, actionData)` but was receiving a single object `{action: 'delete', message: {...}}`
- **Fix**: Updated the function to properly handle the event object:
```javascript
async function handleMessageAction(actionData) {
  const { action, message, newContent } = typeof actionData === 'object' && actionData.action
    ? actionData
    : { action: actionData, message: arguments[1], newContent: arguments[2]?.newContent }
  
  if (!message) {
    console.error('Message is undefined for action:', action)
    alert('Failed to perform action: Message is missing.')
    return
  }
  // ... rest of the function
}
```

### 2. Incorrect Payload Field Name
**File**: `Frontend/src/composables/useMessageActions.js`
- **Issue**: The `editMessage` function was sending `content: newContent` but the backend expected `new_content`
- **Fix**: Changed the payload field name:
```javascript
const payload = {
  action: 'edit_message',
  message_id: message.id,
  new_content: newContent  // Changed from 'content' to 'new_content'
}
```

### 3. WebSocket Event Type Not Recognized
**File**: `Frontend/src/components/alumni/messaging/ChatArea.vue`
- **Issue**: The frontend was looking for `'chat_message_edit'` and `'chat_message_delete'` but the backend sends `'message_edited'` and `'message_deleted'`
- **Fix**: Updated event type checks and properly extract data:
```javascript
// Message edited
if (eventType === 'message_edited' || eventType === 'chat_message_edit' || eventType === 'message_edit') {
  const messageId = data.message_id
  const newContent = data.new_content
  const editedAt = data.edited_at
  
  if (messageId) {
    const idx = props.messages?.findIndex(m => String(m.id) === String(messageId))
    if (idx !== -1) {
      const updatedMessage = {
        ...props.messages[idx],
        content: newContent,
        edited_at: editedAt
      }
      props.messages.splice(idx, 1, updatedMessage)
      console.log('✏️ Applied edit to message:', messageId)
    }
  }
  return
}

// Message deleted
if (eventType === 'message_deleted' || eventType === 'chat_message_delete' || eventType === 'message_delete') {
  const msgId = data.message_id || data.id || (data.message && data.message.id)
  if (msgId) {
    const idx = props.messages?.findIndex(m => String(m.id) === String(msgId))
    if (idx !== -1) {
      props.messages.splice(idx, 1)
      console.log('🗑️ Removed deleted message:', msgId)
    }
  }
  return
}
```

### 4. Private Messages Not Broadcasting to Sender (CRITICAL FIX)
**File**: `Backend/messaging_app/consumers/private_handlers.py`
- **Issue**: For private messages, the backend was excluding the sender from broadcasts and sending them a separate "success" confirmation WITHOUT the updated content. This caused the sender to not see real-time updates.
- **Comparison**: Group messages broadcast to ALL members including the sender, which is why they worked correctly.
- **Fix**: Changed private message handlers to broadcast to ALL participants (including sender), just like group messages:

```python
# OLD CODE (excluded sender):
recipients = [uid for uid in users if uid != self.user.id]
if recipients:
    await self.broadcast_to_users(
        recipients,
        'message_edited',
        {...}
    )
# Send separate success to sender (without content)
await self.send_json({
    'status': 'success',
    'action': 'message_edited',
    'message_id': str(message.id)
})

# NEW CODE (includes sender):
await self.broadcast_to_users(
    users,  # All participants including sender
    'message_edited',
    {
        'message_id': str(message.id),
        'new_content': new_content,
        'edited_at': edited_at.isoformat()
    }
)
```

## Backend Changes
**File**: `Backend/messaging_app/consumers/private_handlers.py`

### Changes Made:
1. **`handle_edit_message`**: Now broadcasts to ALL participants including the sender
2. **`handle_delete_message`**: Now broadcasts to ALL participants including the sender

### Why This Fix Was Needed:
- Group messages already worked correctly because they broadcast to everyone
- Private messages were treating the sender differently, causing real-time update issues
- Now both private and group messages use consistent behavior

## Backend Configuration (Already Correct)
The backend was already correctly configured for routing:
- **Private handlers**: `Backend/messaging_app/consumers/private_handlers.py` - has `handle_edit_message` and `handle_delete_message`
- **Group handlers**: `Backend/messaging_app/consumers/group_handlers.py` - has `handle_group_edit` and `handle_group_delete`
- Both correctly mapped in their respective consumer files

## Testing Instructions

### Test Delete Functionality:
1. Open the messaging interface
2. Send a message to a user or group
3. Click the context menu (three dots) on your own message
4. Click "Delete"
5. Confirm the deletion
6. ✅ The message should disappear from the chat immediately

### Test Edit Functionality:
1. Send a message to a user or group
2. Click the context menu on your own message
3. Click "Edit"
4. Modify the message content
5. Press Enter or click Save
6. ✅ The message content should update immediately
7. ✅ An "(edited)" indicator should appear

### Expected Console Logs:
```
Handling message action: delete for message: <message-id>
Deleting message: <message-id>
🟢 Group WS RECEIVED: {type: 'message_deleted', message_id: '...'}
🗑️ Removed deleted message: <message-id>
```

For edit:
```
Handling message action: edit for message: <message-id>
Editing message: <message-id> New content: <new-content>
🟢 Group WS RECEIVED: {type: 'message_edited', message_id: '...', new_content: '...'}
✏️ Applied edit to message: <message-id>
```

## Files Modified
1. `Frontend/src/composables/useMessageActions.js` - Fixed handleMessageAction signature and editMessage payload
2. `Frontend/src/components/alumni/messaging/ChatArea.vue` - Fixed WebSocket event handling and added enhanced debug logging
3. **`Backend/messaging_app/consumers/private_handlers.py`** - **CRITICAL FIX**: Changed to broadcast to all participants including sender

## Enhanced Debug Logging
Added comprehensive logging to help diagnose any future issues:
- `🔔 ChatArea handleWebSocketMessage received:` - Shows all incoming WebSocket messages
- `✏️ Processing message_edited event:` - Shows when edit events are being processed
- `🗑️ Processing message_deleted event:` - Shows when delete events are being processed
- `✅ Applied edit/delete to message:` - Confirms successful UI update
- `⚠️ Message not found:` - Warns if message couldn't be found in the list

## Date
February 24, 2026

## Summary
The main issue was that **private messages** were not broadcasting edit/delete events to the sender, only sending them a success confirmation without the actual updated data. This meant:
- ❌ Sender: No real-time UI update (message stayed unchanged until refresh)
- ❌ Receiver: Should have gotten the broadcast, but might not have been processing it correctly

The fix ensures that BOTH sender and receiver get the same broadcast event with complete data, making private messages work consistently with group messages where everyone sees real-time updates.
