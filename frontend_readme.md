# Election Comparison System - Frontend & Core Value Guide

## 1. The Core Value Proposition
The core value of the Election Comparison System is **democratizing historical political data**. Raw election data from 1957 to 2026 is incredibly dense, boring, and hard to decipher. 

The frontend's primary job is to transform this massive, 60-year dataset into a beautiful, intuitive, and highly interactive narrative. The system should empower journalists, political analysts, and everyday citizens to uncover hidden trends, swing states, and the rise and fall of political dynasties without needing to look at a single spreadsheet.

## 2. Key Features to Build
To deliver on this core value, the frontend should focus on these highly interactive features:

- **The Macro Dashboard:** A landing page showcasing overall voter turnout, total electorate growth over 60 years, and the shifting power balance of major alliances.
- **Candidate "Time-Machine":** A dedicated search interface where a user can search a specific politician's name and instantly see a timeline of their entire career—which constituencies they contested, their changing vote shares, and their win/loss ratios.
- **Party Dominance & Swing Seat Analyzer:** Visual representations (like stacked area charts or color-coded maps) showing how long a party has held a specific constituency, and highlighting "Swing Seats" that frequently flip.
- **Gender & Demographic Studies:** Charts showing the success rate of female candidates vs male candidates across different decades.

## 3. Design Aesthetics & UX
The design **must feel premium, dynamic, and state-of-the-art**.
- **Color Palette:** Use distinct, meaningful colors for different political parties, wrapped in a sleek, modern UI (consider a robust Dark Mode with subtle glassmorphism effects).
- **Typography:** Use clean, highly readable fonts (like Inter, Roboto, or Outfit) to make data-heavy tables easy to scan.
- **Micro-animations:** Data shouldn't just instantly appear. When a user changes the year filter from 1982 to 2026, the bar charts should smoothly animate and grow/shrink to their new values.
- **Responsiveness:** Analysts will look at this on desktops, but the general public will view it on mobile. Data tables must horizontally scroll or collapse elegantly on smaller screens.

## 4. Recommended Tech Stack
- **Framework:** Next.js (React) or Nuxt (Vue) for fast routing and SEO optimization.
- **Styling:** TailwindCSS for rapid layout, combined with Radix UI or Shadcn for accessible, unstyled component primitives.
- **Data Visualization:** Recharts, Chart.js, or D3.js. (Recharts is highly recommended for React as it handles responsive animations beautifully).
- **Data Fetching:** React Query or SWR to handle fetching data from the backend, caching it in the browser, and keeping the UI fast and snappy.
