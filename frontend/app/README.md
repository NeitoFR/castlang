# CastLang Frontend

This is the frontend application for the CastLang Japanese Podcast Player.

## Environment Configuration

Create a `.env` file in the `frontend/app/` directory with the following configuration:

```env
# API Configuration
PUBLIC_API_URL=http://localhost:8000/api/v1

# Development Configuration
PUBLIC_DEV_MODE=true
PUBLIC_DEBUG=false

# Feature Flags
PUBLIC_ENABLE_DELETE=true
PUBLIC_ENABLE_DOWNLOAD=true
PUBLIC_ENABLE_STREAMING=true
```

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:4321`

### Build for Production

```bash
npm run build
```

## Features

### Podcast Library Management

- **Add Podcasts**: Download audio from YouTube URLs
- **View Library**: Browse all downloaded podcasts with metadata
- **Delete Podcasts**: Remove podcasts from library
- **Download Files**: Download audio files locally

### Audio Player

- **Streaming**: Real-time audio streaming with seeking support
- **Custom Controls**: Play/pause, volume, mute controls
- **Progress Bar**: Visual progress with click-to-seek
- **Metadata Display**: Title, series, duration, file size

### Enhanced Metadata

- **Title**: Podcast title from YouTube
- **Series**: Series name (if available)
- **Episode**: Episode number (if available)
- **Duration**: Audio duration in minutes:seconds
- **File Size**: File size in MB
- **Status**: Download status indicator

## API Integration

The frontend integrates with the CastLang backend API:

### Endpoints Used

- `GET /api/v1/audio-files` - List all audio files
- `GET /api/v1/audio-files/{id}` - Get specific audio file details
- `POST /api/v1/extract-audio` - Download audio from YouTube URL
- `DELETE /api/v1/audio-files/{id}` - Delete audio file
- `GET /api/v1/stream/{filename}` - Stream audio file
- `GET /api/v1/download/{filename}` - Download audio file

### Data Structure

The frontend expects audio files with the following structure:

```typescript
interface AudioFile {
  id: number;
  filename: string;
  original_url: string;
  title?: string;
  episode_number?: number;
  series_name?: string;
  duration_seconds?: number;
  file_size_bytes?: number;
  file_path: string;
  status: string;
  created_at: string;
  updated_at: string;
}
```

## Environment Variables

| Variable                  | Default                        | Description                    |
| ------------------------- | ------------------------------ | ------------------------------ |
| `PUBLIC_API_URL`          | `http://localhost:8000/api/v1` | Backend API base URL           |
| `PUBLIC_DEV_MODE`         | `true`                         | Development mode flag          |
| `PUBLIC_DEBUG`            | `false`                        | Debug mode flag                |
| `PUBLIC_ENABLE_DELETE`    | `true`                         | Enable delete functionality    |
| `PUBLIC_ENABLE_DOWNLOAD`  | `true`                         | Enable download functionality  |
| `PUBLIC_ENABLE_STREAMING` | `true`                         | Enable streaming functionality |

## Tech Stack

- **Astro**: Static site generator
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Vanilla JavaScript**: Interactivity
- **HTML5 Audio API**: Audio playback

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development Notes

### API Error Handling

The frontend includes comprehensive error handling for API calls:

- Network errors
- HTTP error responses
- Invalid data formats
- Backend service unavailability

### Responsive Design

The interface is fully responsive and works on:

- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

### Accessibility

- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management

```sh
npm create astro@latest -- --template minimal
```

[![Open in StackBlitz](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](https://stackblitz.com/github/withastro/astro/tree/latest/examples/minimal)
[![Open with CodeSandbox](https://assets.codesandbox.io/github/button-edit-lime.svg)](https://codesandbox.io/p/sandbox/github/withastro/astro/tree/latest/examples/minimal)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/withastro/astro?devcontainer_path=.devcontainer/minimal/devcontainer.json)

> 🧑‍🚀 **Seasoned astronaut?** Delete this file. Have fun!

## 🚀 Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
/
├── public/
├── src/
│   └── pages/
│       └── index.astro
└── package.json
```

Astro looks for `.astro` or `.md` files in the `src/pages/` directory. Each page is exposed as a route based on its file name.

There's nothing special about `src/components/`, but that's where we like to put any Astro/React/Vue/Svelte/Preact components.

Any static assets, like images, can be placed in the `public/` directory.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Installs dependencies                            |
| `npm run dev`             | Starts local dev server at `localhost:4321`      |
| `npm run build`           | Build your production site to `./dist/`          |
| `npm run preview`         | Preview your build locally, before deploying     |
| `npm run astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `npm run astro -- --help` | Get help using the Astro CLI                     |

## 👀 Want to learn more?

Feel free to check [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).
