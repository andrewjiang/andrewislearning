#!/usr/bin/env node
import fs from 'fs/promises';
import os from 'os';
import path from 'path';
import {fileURLToPath} from 'url';
import {bundle} from '@remotion/bundler';
import {selectComposition, renderMedia} from '@remotion/renderer';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const parseArgs = () => {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log('usage: node captioner/render-captioned.mjs --config <captions.json>');
    process.exit(0);
  }
  const configIndex = args.indexOf('--config');
  if (configIndex === -1 || !args[configIndex + 1]) {
    throw new Error('usage: node captioner/render-captioned.mjs --config <captions.json>');
  }
  return {configPath: path.resolve(args[configIndex + 1])};
};

const exists = async (filePath) => {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
};

const copyIntoPublicDir = async (sourceVideo, publicDir) => {
  const ext = path.extname(sourceVideo) || '.mp4';
  const targetName = `source${ext}`;
  const targetPath = path.join(publicDir, targetName);
  await fs.copyFile(sourceVideo, targetPath);
  return targetName;
};

const copyAssetIntoPublicDir = async (assetPath, publicDir, prefix) => {
  if (!assetPath) {
    return assetPath;
  }
  const resolved = path.resolve(assetPath);
  if (!(await exists(resolved))) {
    return assetPath;
  }
  const ext = path.extname(resolved) || '.png';
  const targetName = `${prefix}${ext}`;
  await fs.copyFile(resolved, path.join(publicDir, targetName));
  return targetName;
};

const copyOverlayAssets = async (overlays, publicDir) => {
  const input = overlays || [];
  const output = [];
  for (const [index, overlay] of input.entries()) {
    const next = {...overlay};
    if (next.avatar) {
      next.avatar = await copyAssetIntoPublicDir(next.avatar, publicDir, `overlay-${index}-avatar`);
    }
    if (next.typingSound) {
      next.typingSound = await copyAssetIntoPublicDir(next.typingSound, publicDir, `overlay-${index}-typing`);
    }
    if (next.typingTrack) {
      next.typingTrack = await copyAssetIntoPublicDir(next.typingTrack, publicDir, `overlay-${index}-typing-track`);
    }
    if (next.slamSound) {
      next.slamSound = await copyAssetIntoPublicDir(next.slamSound, publicDir, `overlay-${index}-slam`);
    }
    if (next.cutSound) {
      next.cutSound = await copyAssetIntoPublicDir(next.cutSound, publicDir, `overlay-${index}-cut`);
    }
    if (next.fontFile) {
      next.fontFile = await copyAssetIntoPublicDir(next.fontFile, publicDir, `overlay-${index}-font`);
    }
    if (Array.isArray(next.frames)) {
      const copiedFrames = [];
      for (const [frameIndex, framePath] of next.frames.entries()) {
        copiedFrames.push(await copyAssetIntoPublicDir(framePath, publicDir, `overlay-${index}-frame-${frameIndex}`));
      }
      next.frames = copiedFrames;
    }
    output.push(next);
  }
  return output;
};

const main = async () => {
  const {configPath} = parseArgs();
  const payload = JSON.parse(await fs.readFile(configPath, 'utf8'));
  const sourceVideo = path.resolve(payload.sourceVideo);
  const output = path.resolve(payload.output);

  if (!(await exists(sourceVideo))) {
    throw new Error(`source video not found: ${sourceVideo}`);
  }

  await fs.mkdir(path.dirname(output), {recursive: true});
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'content-copilot-captioner-'));
  const publicDir = path.join(tmpDir, 'public');
  const outDir = path.join(tmpDir, 'bundle');
  await fs.mkdir(publicDir, {recursive: true});

  try {
    const videoFileName = await copyIntoPublicDir(sourceVideo, publicDir);
    const overlays = await copyOverlayAssets(payload.overlays, publicDir);
    const inputProps = {
      videoFileName,
      width: payload.width,
      height: payload.height,
      fps: payload.fps,
      duration: payload.duration,
      pages: payload.pages,
      overlays,
      safeZone: payload.safeZone,
      style: payload.style,
      captionVariant: payload.captionVariant,
    };

    const serveUrl = await bundle({
      entryPoint: path.join(__dirname, 'src', 'index.jsx'),
      rootDir: __dirname,
      publicDir,
      outDir,
      webpackOverride: (config) => config,
    });

    const composition = await selectComposition({
      serveUrl,
      id: 'CaptionedVideo',
      inputProps,
      timeoutInMilliseconds: 120000,
    });

    await renderMedia({
      composition,
      serveUrl,
      codec: 'h264',
      audioCodec: 'aac',
      crf: Number.isFinite(payload.crf) ? payload.crf : 16,
      x264Preset: payload.x264Preset || 'slow',
      audioBitrate: payload.audioBitrate || '256k',
      outputLocation: output,
      inputProps,
      pixelFormat: 'yuv420p',
      colorSpace: payload.colorSpace || 'bt709',
      overwrite: true,
      logLevel: 'warn',
      timeoutInMilliseconds: 120000,
      chromiumOptions: {
        gl: 'angle',
      },
    });
  } finally {
    await fs.rm(tmpDir, {recursive: true, force: true});
  }
};

main().catch((err) => {
  console.error(`[captioner] ${err.stack || err.message}`);
  process.exit(1);
});
