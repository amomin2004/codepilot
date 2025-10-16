# CodePilot Frontend

Next.js frontend for the CodePilot semantic code search engine.

## Features

- 🔍 **Semantic Search UI** - Natural language search interface
- 🎨 **Modern Design** - Clean, responsive UI with Tailwind CSS
- 🎯 **Advanced Filters** - Filter by path, language, and result count
- 💎 **Syntax Highlighting** - Beautiful code previews
- 📊 **Real-time Status** - System health and indexing status
- ⚡ **Fast & Responsive** - Optimized for performance

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **React Syntax Highlighter** - Code syntax highlighting

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- CodePilot API server running on http://localhost:8000

### Installation

```bash
cd web
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Configuration

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Pages

### `/` - Search Page
- Semantic search interface
- Advanced filters (path, language)
- Real-time search results
- Syntax-highlighted code previews

### `/ingest` - Ingestion Page
- Repository indexing interface
- Advanced chunking options
- System status monitoring
- Ingestion progress tracking

## Components

- **Navigation** - Top navigation with active states
- **SearchForm** - Search input with filters
- **ResultsList** - Search results with syntax highlighting
- **StatusIndicator** - System health status

## API Integration

The frontend communicates with the FastAPI backend via:

- `GET /search` - Semantic code search
- `GET /status` - System status
- `POST /ingest` - Repository ingestion
- `GET /health` - Health check

See `src/lib/api.ts` for the complete API client.

## Build & Deploy

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Development Notes

- Uses Next.js App Router (app directory)
- TypeScript for type safety
- Tailwind CSS for styling
- Responsive design (mobile-first)
- Client-side state management
- Error handling and loading states