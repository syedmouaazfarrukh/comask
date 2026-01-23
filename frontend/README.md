# Energy Compliance Checker - Frontend

A modern, minimalistic frontend for the Colorado Energy Compliance Checker built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🗺️ **Interactive Map**: World map with smooth zoom animation to Colorado
- 💬 **Chat Interface**: ChatGPT-style conversation interface
- 📍 **Location Selection**: Dropdown to select Colorado (expandable to other states)
- 🔄 **Real-time Visualization**: Map shows data sources being queried during processing
- 📚 **Citations**: Answers include source citations with links
- 🎨 **Minimalistic Design**: Clean, elegant UI with subtle energy-themed gradients

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main page with state management
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── LocationSelector.tsx    # Location dropdown
│   ├── WorldMap.tsx            # Map with zoom animation
│   ├── ChatInterface.tsx       # Main chat component
│   ├── ChatMessage.tsx         # Individual message component
│   ├── ThinkingIndicator.tsx  # Loading state
│   └── MapVisualization.tsx    # Sidebar map with data sources
└── package.json
```

## User Flow

1. **Onboarding**: User sees "Ask away" screen with location selector
2. **Location Selection**: User selects Colorado from dropdown
3. **Map Zoom**: World map animates and zooms into Colorado
4. **Chat Interface**: Chat interface opens with welcome message
5. **Question**: User asks a question about Colorado energy regulations
6. **Processing**: 
   - Thinking indicator shows
   - Map visualization sidebar appears
   - Data sources light up on map as they're queried
7. **Answer**: Response appears with citations

## Mock Data

Currently using mock data for:
- Chat responses
- Citations
- Data sources (Colorado Public Utilities Commission, Colorado Energy Office, etc.)

These will be replaced with real API calls when the backend is ready.

## Styling

The design follows a minimalistic, elegant approach:
- Subtle blue/cyan/teal gradients (energy-themed)
- Clean white cards with subtle shadows
- Smooth animations and transitions
- ChatGPT-inspired chat interface
- Responsive design

## Next Steps

- [ ] Connect to backend API
- [ ] Add authentication
- [ ] Implement real-time updates
- [ ] Add more states (beyond Colorado)
- [ ] Enhance map visualization with real coordinates
- [ ] Add query history
- [ ] Export functionality
