# MFE_DEV_MODE User Guide

## Quick Start

### Scenario 1: Quick Development Without Hot-Reload

You want to iterate on an MFE quickly without dealing with Docker mount configuration.

```bash
# Enable profile and authn MFEs as individual dev services
tutor config save --set MFE_DEV_MODE='["profile", "authn"]'

# Launch environment
tutor dev launch

# Start the MFE you're working on
tutor dev start profile

# Access at http://apps.local.openedx.io:1995/profile/u/admin
```

**Pros:**
- No mount configuration needed
- Each MFE starts as a separate service
- Simple and straightforward

**Cons:**
- Code changes require service restart
- No hot-reload capability

---

### Scenario 2: Full Development with Hot-Reload

You want hot-reload for faster iteration during active development.

```bash
# Configure dev mode
tutor config save --set MFE_DEV_MODE='["profile"]'

# Mount your local fork
tutor mounts add /path/to/your/frontend-app-profile

# Launch
tutor dev launch

# Start with hot-reload
tutor dev start profile

# Edit files, changes auto-reload in browser
```

**Pros:**
- Instant feedback on code changes
- No service restarts needed
- True development experience

**Cons:**
- Mount setup required
- Slight performance overhead from volume mounting

---

### Scenario 3: Focused Development on Multiple MFEs

You're working on features across multiple MFEs. One needs hot-reload, others don't.

```bash
# Enable multiple MFEs for dev mode
tutor config save --set MFE_DEV_MODE='["profile", "authn", "learning"]'

# Mount only the one you're actively developing
tutor mounts add /path/to/frontend-app-learning

# Launch
tutor dev launch

# Start services
tutor dev start profile      # Pre-built image, no hot-reload
tutor dev start authn        # Pre-built image, no hot-reload
tutor dev start learning     # Mounted code, hot-reload enabled
```

**Pros:**
- Selective hot-reload
- Focused development with quick switching
- Resource efficient

**Cons:**
- Need to restart services when switching focus

---

### Scenario 4: Progressive Addition to Dev Mode

You're working on one MFE but might need to work on others.

```bash
# Start with just one MFE
tutor config save --set MFE_DEV_MODE='["profile"]'
tutor mounts add /path/to/frontend-app-profile
tutor dev launch
tutor dev start profile

# Later, you also need to work on authn
tutor config save --set MFE_DEV_MODE='["profile", "authn"]'
tutor dev launch  # Rebuilds with new service

# Add mount for authn if needed
tutor mounts add /path/to/frontend-app-authn
tutor dev launch  # Rebuilds with mount

tutor dev start authn
```

**Pros:**
- Incremental development
- Flexible workflow
- No unnecessary complexity upfront

**Cons:**
- Requires multiple `tutor dev launch` commands

---

## Configuration Reference

### Basic Configuration

```bash
# Single MFE
tutor config save --set MFE_DEV_MODE='["profile"]'

# Multiple MFEs
tutor config save --set MFE_DEV_MODE='["profile", "authn", "learning", "account"]'

# Empty (default, uses shared mfe service)
tutor config save --set MFE_DEV_MODE='[]'
```

### View Current Configuration

```bash
tutor config printvalue MFE_DEV_MODE
# Output: ["profile", "authn"]
```

### Reset to Default

```bash
tutor config save --set MFE_DEV_MODE='[]'
```

---

## Service Accessibility

### MFEs in Dev Mode (Individual Services)

When an MFE is in `MFE_DEV_MODE`, it has its own service running on a dedicated port:

| MFE | Port | URL |
|-----|------|-----|
| profile | 1995 | http://apps.local.openedx.io:1995/profile/u/admin |
| authn | 1999 | http://apps.local.openedx.io:1999/ |
| learning | 2000 | http://apps.local.openedx.io:2000/course/... |
| account | 1997 | http://apps.local.openedx.io:1997/account |

Refer to `tutormfe/plugin.py` CORE_MFE_APPS for all ports.

### Other MFEs (Shared mfe Service)

MFEs NOT in `MFE_DEV_MODE` are served by the shared `mfe` service on port 8002:

```
http://apps.local.openedx.io:8002/<mfe-name>/...
```

---

## Working Directory Structure

### Without Mounting

```
tutor-env/
├── plugins/
│   └── mfe/build/mfe/
│       └── Dockerfile (builds all dev images)
└── apps/
    └── mfe/ (shared service)
```

All MFE code is inside the Docker image.

### With Mounting

```
~/projects/
├── frontend-app-profile/  ← Mounted at /openedx/app in profile service
├── frontend-app-learning/
└── ...

tutor-env/
├── plugins/
│   └── mfe/build/mfe/
│       └── Dockerfile
└── apps/
    └── mfe/ (shared service)
```

Mounted code appears inside the service container via Docker volume.

---

## Troubleshooting

### "Service not found" Error

```bash
$ tutor dev start profile
profile: no such service
```

**Solution:** Add profile to `MFE_DEV_MODE`:

```bash
tutor config save --set MFE_DEV_MODE='["profile"]'
tutor dev launch
tutor dev start profile
```

---

### Changes Not Appearing

**Without mount (pre-built image):**
- Need to restart the service: `tutor dev restart profile`
- Or rebuild the image: `tutor images build profile-dev`

**With mount (should have hot-reload):**
- Check that the mount is active: `tutor mounts list`
- Check browser console for errors
- Sometimes need to clear browser cache

---

### Port Conflicts

If port 1995 (profile) is already in use:

```bash
# Check what's using the port
sudo lsof -i :1995

# Change LMS_HOST or use different port by rebuilding
# (Advanced: would require custom Docker setup)
```

---

### Build Failures

If you get OOM errors during image building:

```bash
cat >buildkitd.toml <<EOF
[worker.oci]
  max-parallelism = 1
EOF
docker buildx create --use --name=singlecpu --config=./buildkitd.toml
tutor dev launch
```

---

## Performance Tips

1. **Selective Dev Mode**: Only add MFEs you're actively developing to avoid unnecessary image builds
2. **Mounting Over Rebuilds**: Use mounting for hot-reload instead of restarting services
3. **Batch Changes**: When making many changes, disable hot-reload temporarily and batch restart once
4. **Resource Limits**: Monitor Docker memory usage if building multiple dev images

---

## Integration with IDEs

### VS Code

1. Mount your MFE repository
2. Open the folder in VS Code
3. Install ESLint, Prettier extensions
4. Changes auto-reflect in service with hot-reload

### WebStorm

1. Mount your MFE repository
2. Open the folder as project
3. Configure Language & Frameworks for Node.js
4. Set up deployment to sync with container (optional)

---

## Common Workflows

### Feature Development

```bash
# 1. Setup
tutor config save --set MFE_DEV_MODE='["learning"]'
tutor mounts add ~/projects/frontend-app-learning
tutor dev launch

# 2. Start service
tutor dev start learning

# 3. Edit code in ~/projects/frontend-app-learning
#    Changes appear automatically with hot-reload

# 4. Test and commit
git -C ~/projects/frontend-app-learning add .
git -C ~/projects/frontend-app-learning commit -m "Feature: xyz"
git -C ~/projects/frontend-app-learning push
```

### Bug Fix

```bash
# 1. Quick fix without mount
tutor config save --set MFE_DEV_MODE='["profile"]'
tutor dev launch
tutor dev start profile

# 2. Apply fix in image/source
# (Either via docker exec or by modifying image build)

# 3. Restart service
tutor dev restart profile

# 4. Test
# Verify fix at http://apps.local.openedx.io:1995/profile/u/admin
```

### Dependency Update

```bash
# 1. Update in mounted repo
cd ~/projects/frontend-app-learning
npm install @edx/new-package@latest

# 2. Rebuild image with updated dependencies
tutor images build learning-dev

# 3. Restart service
tutor dev restart learning
```

---

## Migration from Mounting-Only Approach

If you previously relied on mounting only:

```bash
# Old workflow (still works)
tutor mounts add /path/to/frontend-app-profile
tutor dev launch

# New explicit workflow
tutor config save --set MFE_DEV_MODE='["profile"]'
tutor mounts add /path/to/frontend-app-profile
tutor dev launch

# Or without mounting
tutor config save --set MFE_DEV_MODE='["profile"]'
tutor dev launch
# Works but no hot-reload
```

The old approach still works! The new `MFE_DEV_MODE` just makes it explicit and optional.
