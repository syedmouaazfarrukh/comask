# Data Collection UI - Frontend

## ✅ What Was Added

### 1. **Data Collection API Functions** (`lib/api.ts`)
- `startDataCollection()` - Start collection from all sources
- `startSourceCollection()` - Start collection from specific source
- `getDataStats()` - Get document statistics

### 2. **Data Collection Button** (MapVisualization Component)
- Button appears when no data is available
- Shows collection status
- Displays document count after collection
- Auto-refreshes stats

### 3. **Database Status Display**
- Shows current document count
- Lists available sources
- Refresh button to update stats

## 🎯 How to Use

### From the Frontend:

1. **Open the Processing Sidebar**
   - Submit a query (even if no data)
   - Right sidebar will open showing "No Data Available"

2. **Click "Collect Data" Button**
   - Button is in the yellow warning box
   - Shows "Collecting..." while running
   - Takes 5-10 minutes

3. **Check Status**
   - Status message shows progress
   - After completion, stats will update
   - Document count will appear

4. **Refresh Stats**
   - Click "Refresh" button in Database Status section
   - Updates document count

### What Happens:

1. **Button Click** → Calls `POST /api/data/collect`
2. **Backend Starts** → Scrapers run in background
3. **Status Updates** → Shows "Data collection started in background"
4. **Stats Refresh** → After 2 seconds, fetches updated stats

## 📊 UI Features

### When No Data:
- ⚠️ Yellow warning box
- "Collect Data" button
- Status messages
- Help text

### When Data Available:
- ✅ Database Status section
- Document count
- Source list
- Refresh button

### During Collection:
- 🔄 Loading spinner
- Status message
- "This may take 5-10 minutes" note

## 🔧 API Endpoints Used

- `POST /api/data/collect?jurisdiction=colorado` - Start collection
- `GET /api/data/stats?jurisdiction=colorado` - Get stats

## 💡 Tips

- **Collection runs in background** - You can continue using the app
- **Check stats** - Use refresh button to see progress
- **First time** - May take 5-10 minutes
- **Subsequent collections** - Faster (only new documents)

## 🐛 Troubleshooting

- **Button doesn't work**: Check backend is running
- **No status update**: Check browser console for errors
- **Stats not updating**: Click refresh button
- **Collection fails**: Check backend logs

