#!/usr/bin/env node
import fs from 'fs/promises';
import os from 'os';
import path from 'path';
import {spawnSync} from 'child_process';
import {fileURLToPath} from 'url';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const labelFontPath = '/System/Library/Fonts/Supplemental/Arial Bold.ttf';

const candidates = [
  {id: 'bebas-neue', label: 'Bebas Neue', fontFamily: 'Slam Bebas Neue', fontWeight: 400, fontSize: 292, fontFile: '.context/fonts/BebasNeue-Regular.ttf'},
  {id: 'anton', label: 'Anton', fontFamily: 'Slam Anton', fontWeight: 400, fontSize: 292, fontFile: '.context/fonts/Anton-Regular.ttf'},
  {id: 'antonio', label: 'Antonio', fontFamily: 'Slam Antonio', fontWeight: 700, fontSize: 302, fontFile: '.context/fonts/Antonio-Bold.ttf'},
  {id: 'big-shoulders', label: 'Big Shoulders', fontFamily: 'Slam Big Shoulders', fontWeight: 900, fontSize: 306, fontFile: '.context/fonts/BigShoulders-Black.ttf'},
  {id: 'barlow-condensed', label: 'Barlow Condensed', fontFamily: 'Slam Barlow Condensed', fontWeight: 900, fontSize: 294, fontFile: '.context/fonts/BarlowCondensed-Black.ttf'},
  {id: 'league-gothic', label: 'League Gothic', fontFamily: 'Slam League Gothic', fontWeight: 400, fontSize: 320, fontFile: '.context/fonts/LeagueGothic-Regular.ttf'},
  {id: 'oswald', label: 'Oswald', fontFamily: 'Slam Oswald', fontWeight: 700, fontSize: 292, fontFile: '.context/fonts/Oswald-Bold.ttf'},
  {id: 'teko', label: 'Teko', fontFamily: 'Slam Teko', fontWeight: 700, fontSize: 326, fontFile: '.context/fonts/Teko-Bold.ttf'},
  {id: 'archivo-black', label: 'Archivo Black', fontFamily: 'Slam Archivo Black', fontWeight: 400, fontSize: 292, fontFile: '.context/fonts/ArchivoBlack-Regular.ttf'},
];

const parseArgs = () => {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log('usage: node captioner/render-slam-font-lab.mjs --config <captions.json> [--out-dir <dir>] [--frame <n>]');
    process.exit(0);
  }
  const valueAfter = (flag, fallback) => {
    const index = args.indexOf(flag);
    return index === -1 ? fallback : args[index + 1];
  };
  const configPath = valueAfter('--config', '.context/day_two_slam_preview.json');
  return {
    configPath: path.resolve(configPath),
    outDir: path.resolve(valueAfter('--out-dir', '.context/previews/slam_font_lab')),
    frame: Number(valueAfter('--frame', 8)),
  };
};

const exists = async (filePath) => {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
};

const copySourceVideo = async (sourceVideo, publicDir) => {
  const ext = path.extname(sourceVideo) || '.mp4';
  const targetName = `source${ext}`;
  await fs.copyFile(sourceVideo, path.join(publicDir, targetName));
  return targetName;
};

const copyAssetIntoPublicDir = async (assetPath, publicDir, prefix) => {
  const resolved = path.resolve(assetPath);
  if (!(await exists(resolved))) {
    throw new Error(`asset not found: ${resolved}`);
  }
  const ext = path.extname(resolved) || '.ttf';
  const targetName = `${prefix}${ext}`;
  await fs.copyFile(resolved, path.join(publicDir, targetName));
  return targetName;
};

const run = (command, args) => {
  const result = spawnSync(command, args, {stdio: 'inherit'});
  if (result.status !== 0) {
    throw new Error(`${command} failed with exit code ${result.status}`);
  }
};

const labelStill = async ({input, output, label}) => {
  const magickArgs = [
    input,
    '-resize',
    '360x640^',
    '-gravity',
    'center',
    '-extent',
    '360x640',
    '-background',
    '#101010',
    '-gravity',
    'south',
    '-splice',
    '0x76',
    '-gravity',
    'south',
    '-font',
    labelFontPath,
    '-pointsize',
    '26',
    '-fill',
    '#FFFFFF',
    '-annotate',
    '+0+22',
    label,
    output,
  ];
  run('magick', magickArgs);
};

const main = async () => {
  const {configPath, outDir, frame} = parseArgs();
  const payload = JSON.parse(await fs.readFile(configPath, 'utf8'));
  const sourceVideo = path.resolve(payload.sourceVideo);
  if (!(await exists(sourceVideo))) {
    throw new Error(`source video not found: ${sourceVideo}`);
  }

  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'content-copilot-font-lab-'));
  const publicDir = path.join(tmpDir, 'public');
  const bundleDir = path.join(tmpDir, 'bundle');
  await fs.mkdir(publicDir, {recursive: true});
  await fs.mkdir(outDir, {recursive: true});

  try {
    const videoFileName = await copySourceVideo(sourceVideo, publicDir);
    const preparedCandidates = [];
    for (const candidate of candidates) {
      preparedCandidates.push({
        ...candidate,
        publicFontFile: await copyAssetIntoPublicDir(candidate.fontFile, publicDir, `font-${candidate.id}`),
      });
    }
    const baseOverlay = (payload.overlays || []).find((overlay) => overlay.type === 'slam_title') || {
      type: 'slam_title',
      start: 0.15,
      end: 2.65,
      text: 'DAY TWO',
    };

    const makeInputProps = (candidate) => ({
      videoFileName,
      width: payload.width,
      height: payload.height,
      fps: payload.fps,
      duration: payload.duration,
      pages: [],
      overlays: [
        {
          ...baseOverlay,
          slamSound: null,
          fontFamily: candidate.fontFamily,
          fontWeight: candidate.fontWeight,
          fontFile: candidate.publicFontFile,
          fontSize: candidate.fontSize,
          widthPercent: 0.94,
        },
      ],
      safeZone: payload.safeZone,
      style: payload.style,
      captionVariant: payload.captionVariant,
    });

    const serveUrl = await bundle({
      entryPoint: path.join(__dirname, 'src', 'index.jsx'),
      rootDir: __dirname,
      publicDir,
      outDir: bundleDir,
      webpackOverride: (config) => config,
    });
    const composition = await selectComposition({
      serveUrl,
      id: 'CaptionedVideo',
      inputProps: makeInputProps(preparedCandidates[0]),
      timeoutInMilliseconds: 120000,
    });

    const manifest = [];
    const labeledStills = [];
    for (const [index, candidate] of preparedCandidates.entries()) {
      const number = String(index + 1).padStart(2, '0');
      const stillPath = path.join(outDir, `${number}-${candidate.id}.png`);
      const labeledPath = path.join(outDir, `${number}-${candidate.id}-labeled.png`);
      await renderStill({
        composition,
        serveUrl,
        output: stillPath,
        frame,
        inputProps: makeInputProps(candidate),
        imageFormat: 'png',
        overwrite: true,
        logLevel: 'warn',
        timeoutInMilliseconds: 120000,
        chromiumOptions: {
          gl: 'angle',
        },
      });
      await labelStill({
        input: stillPath,
        output: labeledPath,
        label: `${number}. ${candidate.label}`,
      });
      labeledStills.push(labeledPath);
      manifest.push({
        ...candidate,
        publicFontFile: undefined,
        still: path.relative(process.cwd(), stillPath),
        labeledStill: path.relative(process.cwd(), labeledPath),
      });
    }

    const contactSheet = path.join(outDir, 'contact-sheet.png');
    run('magick', [
      'montage',
      '-font',
      labelFontPath,
      '+label',
      ...labeledStills,
      '-tile',
      '3x3',
      '-geometry',
      '+18+18',
      '-background',
      '#101010',
      contactSheet,
    ]);
    await fs.writeFile(
      path.join(outDir, 'manifest.json'),
      `${JSON.stringify({frame, contactSheet: path.relative(process.cwd(), contactSheet), candidates: manifest}, null, 2)}\n`,
    );
    console.log(`[font-lab] wrote ${path.relative(process.cwd(), contactSheet)}`);
  } finally {
    await fs.rm(tmpDir, {recursive: true, force: true});
  }
};

main().catch((err) => {
  console.error(`[font-lab] ${err.stack || err.message}`);
  process.exit(1);
});
