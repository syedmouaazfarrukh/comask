'use client';

export default function WorldMapBackground() {
  // Clean world map SVG with proper continent outlines
  return (
    <div className="w-full h-full opacity-25">
      <svg
        viewBox="0 0 2000 1000"
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
        style={{ filter: 'blur(0.5px)' }}
      >
        {/* World map paths - cleaner outlines */}
        {/* North America */}
        <path
          d="M 300 200 Q 350 150 450 180 T 600 220 T 700 280 T 750 350 T 700 450 T 600 500 T 450 480 T 300 450 Q 250 400 280 350 Q 270 280 300 200 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-gray-400"
        />
        {/* USA detail */}
        <path
          d="M 400 280 L 500 270 L 550 320 L 520 380 L 450 390 L 400 350 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          className="text-blue-400"
        />
        
        {/* South America */}
        <path
          d="M 500 450 Q 550 440 600 480 T 650 550 T 620 650 T 580 700 T 520 720 Q 480 700 500 650 Q 490 580 500 450 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-gray-400"
        />
        
        {/* Europe */}
        <path
          d="M 800 150 Q 900 140 1000 160 T 1100 200 T 1080 280 T 1000 300 Q 900 290 850 250 Q 820 200 800 150 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-gray-400"
        />
        
        {/* Africa */}
        <path
          d="M 900 300 Q 1000 290 1100 320 T 1150 450 T 1120 600 T 1050 700 Q 950 680 900 600 Q 880 500 900 300 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-gray-400"
        />
        
        {/* Asia */}
        <path
          d="M 1100 100 Q 1300 90 1500 120 T 1700 200 T 1650 350 T 1550 450 T 1400 480 Q 1200 460 1100 400 Q 1050 300 1100 100 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-gray-400"
        />
        
        {/* Australia */}
        <path
          d="M 1400 600 Q 1500 590 1600 620 T 1650 700 Q 1600 750 1500 760 Q 1400 740 1400 600 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-gray-400"
        />
      </svg>
    </div>
  );
}
