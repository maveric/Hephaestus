# Configuring Hephaestus for Remote Access

This guide explains how to configure Hephaestus to be accessible from a custom IP address instead of localhost.

## Overview

By default, Hephaestus runs with:
- Backend API on `http://localhost:8000`
- Frontend UI on `http://localhost:5173`
- WebSocket connections to `ws://localhost:8000/ws`

This configuration allows you to change these to use a custom IP address (e.g., `192.168.1.100`) so you can access Hephaestus from other devices on your network.

## Backend Configuration

### 1. Create or Update `.env` File

In the root directory of the project, create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

### 2. Set Host IP Configuration

Edit `.env` and update these values:

```bash
# Set this to your machine's IP address
HOST_IP=192.168.1.100

# Configure CORS to allow your frontend to connect
# Use comma-separated list of allowed origins
CORS_ALLOWED_ORIGINS=http://192.168.1.100:5173,http://localhost:5173

# Backend will still bind to all interfaces (0.0.0.0) to accept connections
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

### Configuration Options:

- **`HOST_IP`**: The IP address or domain where your backend is accessible
  - Examples: `192.168.1.100`, `localhost`, `your-domain.com`
  
- **`CORS_ALLOWED_ORIGINS`**: Comma-separated list of allowed origins for CORS
  - Use `*` to allow all origins (not recommended for production)
  - Examples: `http://192.168.1.100:5173,http://localhost:5173`
  
- **`MCP_HOST`**: The interface the server binds to (keep as `0.0.0.0` to accept remote connections)

- **`MCP_PORT`**: The port the backend listens on (default: `8000`)

## Frontend Configuration

### 1. Create Frontend `.env` File

In the `frontend/` directory, create a `.env` file:

```bash
cd frontend
cp .env.example .env
```

### 2. Configure API Connection

Edit `frontend/.env`:

```bash
# Backend API Host IP (should match backend HOST_IP)
VITE_API_HOST=192.168.1.100

# Backend API Port (should match backend MCP_PORT)
VITE_API_PORT=8000

# Protocol (http or https)
VITE_API_PROTOCOL=http
```

## Finding Your IP Address

### Linux/Mac:
```bash
# Get local IP address
ip addr show | grep "inet " | grep -v 127.0.0.1

# Or use:
hostname -I | awk '{print $1}'
```

### Windows:
```cmd
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

## Example Configurations

### Local Development (Default)
```bash
# Backend .env
HOST_IP=localhost
CORS_ALLOWED_ORIGINS=*

# Frontend .env
VITE_API_HOST=localhost
VITE_API_PORT=8000
VITE_API_PROTOCOL=http
```

### Local Network Access
```bash
# Backend .env
HOST_IP=192.168.1.100
CORS_ALLOWED_ORIGINS=http://192.168.1.100:5173,http://localhost:5173

# Frontend .env
VITE_API_HOST=192.168.1.100
VITE_API_PORT=8000
VITE_API_PROTOCOL=http
```

### Production Deployment
```bash
# Backend .env
HOST_IP=api.yourdomain.com
CORS_ALLOWED_ORIGINS=https://app.yourdomain.com

# Frontend .env
VITE_API_HOST=api.yourdomain.com
VITE_API_PORT=443
VITE_API_PROTOCOL=https
```

## Starting the Services

### Backend
```bash
# From project root
python run_server.py
```

The server will be accessible at:
- `http://{HOST_IP}:8000` (e.g., `http://192.168.1.100:8000`)

### Frontend
```bash
# From frontend directory
cd frontend
npm run dev
```

The frontend will be accessible at:
- `http://0.0.0.0:5173` (accessible from any IP on your machine)
- `http://192.168.1.100:5173` (your local IP)
- `http://localhost:5173` (localhost)

## Verifying Configuration

### Check Backend Configuration
```bash
python -c "from src.core.simple_config import get_config; config = get_config(); print(f'Host IP: {config.host_ip}'); print(f'CORS Origins: {config.cors_allowed_origins}')"
```

### Test Backend API
```bash
# Replace with your HOST_IP
curl http://192.168.1.100:8000/health
```

### Test Frontend Connection
1. Open browser to `http://192.168.1.100:5173`
2. Check browser console for any CORS errors
3. Verify WebSocket connection in Network tab

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
1. Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. Restart the backend server after changing `.env`
3. Clear browser cache and hard reload (Ctrl+Shift+R)

### WebSocket Connection Failed
1. Check that `VITE_API_HOST` and `VITE_API_PORT` match your backend
2. Verify firewall allows connections on port 8000
3. Check backend logs for connection attempts

### Cannot Access from Other Devices
1. Verify your firewall allows inbound connections on ports 5173 and 8000
2. Ensure you're using the correct IP address (not 127.0.0.1)
3. Check that both devices are on the same network

### Firewall Configuration (Linux)
```bash
# Allow backend port
sudo ufw allow 8000/tcp

# Allow frontend port
sudo ufw allow 5173/tcp
```

## Security Considerations

1. **CORS**: Don't use `CORS_ALLOWED_ORIGINS=*` in production
2. **Firewall**: Only expose ports on trusted networks
3. **HTTPS**: Use HTTPS for production deployments
4. **Authentication**: Consider adding authentication for production use

## Additional Notes

- Changes to `.env` files require restarting the respective service
- Frontend `.env` files are read at build time, so restart `npm run dev` after changes
- The backend `MCP_HOST=0.0.0.0` setting allows the server to accept connections from any interface
- WebSocket connections automatically use the same host/port as HTTP connections
