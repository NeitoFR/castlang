# CastLang Streaming Implementation

This document outlines the podcast streaming functionality implemented in CastLang.

## Features

### Backend Streaming Capabilities

1. **HTTP Range Request Support**: Full support for range requests enabling:
   - Audio seeking/scrubbing
   - Efficient bandwidth usage
   - Resume playback from any position

2. **Streaming Endpoints**:
   - `/stream/{filename}` - Stream audio files with range request support
   - `/download/{filename}` - Download audio files (backward compatibility)
   - `/audio-files` - List available audio files

3. **Optimized Delivery**:
   - 8KB chunk streaming for efficient memory usage
   - Proper MIME type headers (`audio/mpeg`)
   - Content-Length and Accept-Ranges headers

### Frontend Streaming Features

1. **Modern Audio Player**:
   - Native HTML5 audio controls
   - Built-in seeking and volume control
   - Loading states and error handling
   - Clean, responsive design

2. **Enhanced User Experience**:
   - Real-time download feedback
   - Success/error status messages
   - Automatic library refresh after downloads
   - File name formatting (underscores to spaces)

3. **Responsive Design**:
   - Mobile-friendly interface
   - Tailwind CSS styling
   - Accessible controls

## Technical Implementation

### Backend (FastAPI)

The streaming functionality is implemented in `backend/app/src/routes.py`:

```python
@router.get("/stream/{filename}")
async def stream_audio(filename: str, request: Request):
    # Range request handling for seeking
    # Chunk-based streaming for efficiency
    # Error handling for missing files
```

Key features:
- Parses HTTP Range headers
- Returns appropriate status codes (200, 206, 404, 416)
- Streams files in 8KB chunks
- Supports partial content delivery

### Frontend (Astro)

The audio player is implemented in `frontend/app/src/components/AudioPlayer.astro`:

- HTML5 audio element with custom styling
- TypeScript for type safety
- Event handling for audio states
- Error boundary implementation

Updated components:
- `AudioList.astro` - Now renders streaming players
- `DownloadForm.astro` - Enhanced with loading states
- `index.astro` - Updated branding and descriptions

## How to Use

### Starting the Application

1. **Backend**:
   ```bash
   cd backend/app
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend**:
   ```bash
   cd frontend/app
   npm run dev
   ```

### Adding Podcasts

1. Open http://localhost:4321
2. Paste a YouTube URL in the "Add New Podcast" section
3. Click "Download & Add to Library"
4. Wait for the download to complete

### Streaming Podcasts

1. Once downloaded, podcasts appear in "Your Podcast Library"
2. Use the built-in audio controls to:
   - Play/pause
   - Seek to any position
   - Adjust volume
   - Download the file locally

## Testing

Use the provided test script to verify streaming functionality:

```bash
python test_streaming.py
```

This script tests:
- Backend health
- Audio file listing
- Basic streaming
- Range request support

## API Endpoints

### GET /stream/{filename}
Stream an audio file with range request support.

**Parameters:**
- `filename`: The audio file name

**Headers:**
- `Range` (optional): Byte range for partial content

**Response:**
- `200`: Full file stream
- `206`: Partial content (range request)
- `404`: File not found
- `416`: Range not satisfiable

### GET /download/{filename}
Download an audio file.

**Parameters:**
- `filename`: The audio file name

**Response:**
- `200`: File download
- `404`: File not found

## Browser Compatibility

The streaming implementation uses standard HTML5 audio and HTTP range requests, supported by:

- Chrome/Chromium (all versions)
- Firefox (all modern versions)
- Safari (all modern versions)
- Edge (all modern versions)

## Performance Considerations

1. **Memory Usage**: Files are streamed in 8KB chunks to minimize memory footprint
2. **Bandwidth**: Range requests allow efficient seeking without downloading entire files
3. **Concurrent Streams**: FastAPI handles multiple concurrent streams efficiently
4. **Caching**: Browsers will cache audio data automatically

## Security Considerations

1. **File Access**: Only files in the `downloads/` directory can be streamed
2. **Path Traversal**: Filename validation prevents directory traversal attacks
3. **CORS**: Currently allows all origins (should be restricted in production)

## Future Enhancements

Potential improvements:
1. **Playlist Support**: Create and manage playlists
2. **Metadata Extraction**: Show episode titles, descriptions, artwork
3. **User Authentication**: Personal libraries and preferences
4. **Progressive Web App**: Offline listening capabilities
5. **Audio Quality Selection**: Multiple bitrate options
6. **Streaming Analytics**: Track listening statistics

## Troubleshooting

### Common Issues

1. **"Audio file not found"**:
   - Ensure the file exists in `backend/app/downloads/`
   - Check file permissions

2. **Streaming not working**:
   - Verify backend is running on port 8000
   - Check browser console for CORS errors
   - Try refreshing the page

3. **Seeking not working**:
   - Ensure range requests are enabled
   - Check server logs for range request errors

### Debug Steps

1. Check backend logs for errors
2. Use browser dev tools to inspect network requests
3. Run the test script to verify streaming endpoints
4. Verify file permissions in downloads directory

## Contributing

When contributing to streaming functionality:

1. Test with various audio file sizes
2. Verify range request behavior
3. Check mobile device compatibility
4. Update documentation for new features
5. Add appropriate error handling 