# Installation Guide

## Required Dependencies

Install the following packages:

```bash
npm install framer-motion lucide-react --legacy-peer-deps
```

**Note**: The `--legacy-peer-deps` flag is needed because lucide-react may show peer dependency warnings with React 19, but it works correctly.

## Optional: For Enhanced Maps (Future)

If you want to use a more detailed map library later:

```bash
npm install react-simple-maps @react-spring/web
```

## Quick Start

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000)

## Notes

- The current implementation uses simplified SVG-based maps
- For production, consider integrating a proper map library like:
  - `react-simple-maps` for vector maps
  - `@react-spring/web` for advanced animations
  - Or Google Maps / Mapbox for detailed geographic data

