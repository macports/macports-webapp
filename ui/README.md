# MacPorts Modern UI

A beautiful, modern, client-side interface for browsing MacPorts packages, built with Next.js 14, React 18, and Tailwind CSS.

## ✨ Features

### 🏠 **Homepage**
- Hero section with live search functionality
- Quick links to all major sections
- Recently updated ports display
- Popular categories grid
- Responsive design with smooth animations

### 🔍 **Advanced Search**
- Full-text search across all ports
- Real-time autocomplete suggestions
- Search results with relevance scoring
- Pagination for large result sets
- URL-based search queries

### 📦 **Port Browsing**
- Grid and list view modes
- Advanced filtering by category and maintainer
- Sorting by name or last updated
- Detailed port information pages
- Installation commands with copy functionality

### 🏷️ **Categories**
- Browse all port categories
- Search within categories
- Port count for each category
- Direct links to filtered port listings

### 👥 **Maintainers**
- Browse all port maintainers
- GitHub profile integration
- Port count per maintainer
- Search by name, GitHub username, or email

### 📊 **Statistics Dashboard**
- Installation statistics from opt-in users
- Most popular and most requested ports
- Interactive charts and visualizations
- Real-time data from the MacPorts API

### 🎨 **Design System**
- Dark theme with blue accent colors
- Glassmorphism design elements
- Smooth animations and transitions
- Fully responsive layout
- Accessibility-focused components

## 🛠️ Technology Stack

- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **TypeScript**: Full type safety
- **API Integration**: Custom API client for MacPorts REST API

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
ui/
├── app/                    # Next.js App Router pages
│   ├── categories/         # Categories listing page
│   ├── maintainers/        # Maintainers listing page
│   ├── ports/             # Port browsing and detail pages
│   │   └── [name]/        # Dynamic port detail page
│   ├── search/            # Advanced search page
│   ├── stats/             # Statistics dashboard
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Homepage
│   └── globals.css        # Global styles
├── components/            # Reusable React components
│   ├── Header.tsx         # Navigation header
│   ├── Footer.tsx         # Site footer
│   ├── SearchBar.tsx      # Search input with autocomplete
│   ├── HomeRecent.tsx     # Recently updated ports
│   └── QuickLinks.tsx     # Homepage quick links
├── lib/                   # Utility libraries
│   ├── api.ts            # API configuration
│   ├── api-client.ts     # MacPorts API client
│   └── types.ts          # TypeScript type definitions
└── tailwind.config.cjs   # Tailwind CSS configuration
```

## 🔌 API Integration

The application integrates with the live MacPorts API at `https://ports.macports.org/api/v1/` providing:

- **Port Information**: Detailed package metadata, dependencies, variants
- **Search**: Full-text search with autocomplete
- **Categories**: Port organization and browsing
- **Maintainers**: Developer information and port ownership
- **Build History**: CI/CD build status and logs
- **Statistics**: Installation analytics from opt-in users

## 🎯 Key Features Implemented

### Enhanced User Experience
- **Fast Navigation**: Client-side routing with instant page transitions
- **Smart Search**: Real-time autocomplete with keyboard navigation
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Accessibility**: ARIA labels, semantic HTML, keyboard navigation

### Modern Development Practices
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized React components with proper caching
- **Code Quality**: ESLint configuration with strict rules
- **Build Optimization**: Next.js production optimizations

### API Error Handling
- **Graceful Degradation**: Fallback content for API failures
- **Retry Logic**: Automatic retry for failed requests
- **Loading States**: Skeleton screens and progress indicators
- **Error Boundaries**: Comprehensive error handling

## 🌟 Design Highlights

- **Modern Glassmorphism**: Semi-transparent cards with backdrop blur
- **Smooth Animations**: Micro-interactions and hover effects
- **Consistent Typography**: Clear hierarchy and readable fonts
- **Color System**: Brand-consistent blue palette with proper contrast
- **Spacing**: Consistent spacing scale using Tailwind utilities

## 🔮 Future Enhancements

- [ ] User authentication and preferences
- [ ] Favorite ports and watchlists
- [ ] Advanced filtering options
- [ ] Port comparison tools
- [ ] Installation guides and tutorials
- [ ] Dark/light theme toggle
- [ ] Offline support with service workers

## 🤝 Contributing

This is a modern client-side interface for the MacPorts project. Contributions are welcome!

## 📄 License

This project follows the same license as the main MacPorts project.

---

**Live API**: [https://ports.macports.org/api/v1/](https://ports.macports.org/api/v1/)  
**MacPorts Website**: [https://www.macports.org/](https://www.macports.org/)  
**GitHub Repository**: [https://github.com/macports/macports-ports](https://github.com/macports/macports-ports)