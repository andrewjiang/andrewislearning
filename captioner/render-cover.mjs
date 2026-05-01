#!/usr/bin/env node
import fs from 'fs/promises';
import os from 'os';
import path from 'path';
import {fileURLToPath} from 'url';
import {bundle} from '@remotion/bundler';
import {selectComposition, renderStill} from '@remotion/renderer';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const parseArgs = () => {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log('usage: node captioner/render-cover.mjs --image <png> --out <png> [--variant outplayed|day-one]');
    process.exit(0);
  }
  const valueAfter = (flag) => {
    const index = args.indexOf(flag);
    return index === -1 ? null : args[index + 1];
  };
  const image = valueAfter('--image');
  const out = valueAfter('--out');
  if (!image || !out) {
    throw new Error('usage: node captioner/render-cover.mjs --image <png> --out <png> [--variant outplayed|day-one]');
  }
  return {
    imagePath: path.resolve(image),
    outPath: path.resolve(out),
    variant: valueAfter('--variant') || 'outplayed',
  };
};

const main = async () => {
  const {imagePath, outPath, variant} = parseArgs();
  await fs.access(imagePath);
  await fs.mkdir(path.dirname(outPath), {recursive: true});

  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'content-copilot-cover-'));
  const publicDir = path.join(tmpDir, 'public');
  const outDir = path.join(tmpDir, 'bundle');
  await fs.mkdir(publicDir, {recursive: true});

  try {
    const imageFileName = 'cover-source.png';
    await fs.copyFile(imagePath, path.join(publicDir, imageFileName));

    const serveUrl = await bundle({
      entryPoint: path.join(__dirname, 'src', 'index.jsx'),
      rootDir: __dirname,
      publicDir,
      outDir,
      webpackOverride: (config) => config,
    });

    const inputProps = {imageFileName, variant};
    const composition = await selectComposition({
      serveUrl,
      id: 'CoverImage',
      inputProps,
      timeoutInMilliseconds: 120000,
    });

    await renderStill({
      composition,
      serveUrl,
      inputProps,
      output: outPath,
      imageFormat: 'png',
      frame: 0,
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
  console.error(`[cover] ${err.stack || err.message}`);
  process.exit(1);
});
