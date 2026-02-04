# Study with Challenge - Frontend

Modern, interactive frontend for the Study with Challenge learning platform.

## 🛠️ Technology Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Styling**: TailwindCSS 3
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **Code Editor**: Monaco Editor
- **Visualization**: D3.js
- **Icons**: Lucide React

## 📦 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── atoms/          # Basic UI components (Button, Badge, ProgressBar)
│   │   ├── molecules/      # Compound components (ChallengeCard, LevelCard)
│   │   ├── organisms/      # Complex components (Header, CodeViewer)
│   │   ├── templates/      # Page layouts
│   │   └── pages/          # Complete pages
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API client & services
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Helper functions
│   └── styles/             # Global styles
├── public/                 # Static assets
└── index.html              # HTML entry point
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 🎨 Component Library

### Atomic Components

#### Button
```tsx
import { Button } from '@components/atoms/Button'

<Button variant="primary" size="md">Click me</Button>
<Button variant="secondary" isLoading>Loading...</Button>
```

**Variants**: `primary`, `secondary`, `ghost`, `danger`  
**Sizes**: `sm`, `md`, `lg`

#### Badge
```tsx
import { Badge } from '@components/atoms/Badge'
import { Difficulty } from '@types/index'

<Badge variant="difficulty" difficulty={Difficulty.BASIC}>Basic</Badge>
<Badge>Default</Badge>
```

#### ProgressBar
```tsx
import { ProgressBar } from '@components/atoms/ProgressBar'

<ProgressBar current={60} max={100} showLabel showPercentage />
```

## 🌙 Dark Mode

Toggle dark mode by adding `dark` class to `<html>` element:

```typescript
document.documentElement.classList.toggle('dark')
```

## 📱 Responsive Design

Breakpoints:
- `sm`: 640px (Tablet)
- `md`: 768px (Desktop)
- `lg`: 1024px (Wide Desktop)
- `xl`: 1280px (Ultra-wide)

## 🔧 Configuration

### Path Aliases

```typescript
@/*          → ./src/*
@components/* → ./src/components/*
@hooks/*     → ./src/hooks/*
@services/*  → ./src/services/*
@types/*     → ./src/types/*
@utils/*     → ./src/utils/*
```

### API Proxy

Development server proxies `/api` requests to `http://localhost:8000` (backend).

## 🧪 Testing

```bash
npm run test          # Run unit tests
npm run test:coverage # Generate coverage report
npm run lint          # Run ESLint
npm run type-check    # TypeScript type checking
```

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code
- `npm run type-check` - Check TypeScript types

## 🎯 Development Status

### ✅ Completed
- [x] Project setup (Vite + React + TypeScript)
- [x] TailwindCSS configuration
- [x] TypeScript types
- [x] Atomic components (Button, Badge, ProgressBar)
- [x] Component showcase page

### 🚧 In Progress
- [ ] Molecule components
- [ ] Monaco Editor integration
- [ ] D3.js call graph visualization
- [ ] API client
- [ ] Page components

### 📋 Planned
- [ ] Authentication
- [ ] Real-time updates (WebSocket)
- [ ] Accessibility improvements
- [ ] Performance optimization
- [ ] E2E tests

## 📄 License

MIT
