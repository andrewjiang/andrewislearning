import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {fitText} from '@remotion/layout-utils';
import {
  defaultFontFamily,
  displayFontFamily,
  handwrittenFontFamily,
  resolveCaptionFontFamily,
} from './fonts.js';
import {SocialOverlayLayer} from './SocialOverlays.jsx';
import {WorkflowOverlayLayer} from './WorkflowOverlays.jsx';

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const withAlpha = (hex, alpha) => {
  const clean = String(hex || '#000000').replace('#', '');
  if (!/^[0-9a-fA-F]{6}$/.test(clean)) {
    return `rgba(10, 10, 10, ${alpha})`;
  }
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const laneStyle = (anchor, safeZone) => {
  const safe = {
    top: safeZone?.top ?? 0.12,
    bottom: safeZone?.bottom ?? 0.22,
    left: safeZone?.left ?? 0.08,
    right: safeZone?.right ?? 0.08,
  };

  const base = {
    position: 'absolute',
    left: `${safe.left * 100}%`,
    right: `${safe.right * 100}%`,
    display: 'flex',
    justifyContent: 'center',
    textAlign: 'center',
  };

  if (anchor === 'upper_safe') {
    return {...base, top: `${safe.top * 100}%`, alignItems: 'flex-start'};
  }
  if (anchor === 'mid_safe') {
    return {...base, top: '50%', transform: 'translateY(-50%)', alignItems: 'center'};
  }
  if (anchor === 'upper_mid_safe') {
    return {...base, top: '25%', transform: 'translateY(-50%)', alignItems: 'center'};
  }
  return {...base, bottom: `${safe.bottom * 100}%`, alignItems: 'flex-end'};
};

const normalizeText = (text, uppercase) => {
  if (!uppercase) {
    return text;
  }
  return text.toUpperCase();
};

const normalizeWordKey = (text) => String(text || '').toLowerCase().replace(/[^a-z0-9']/g, '');

const weakLeadingWords = new Set([
  'a',
  'an',
  'and',
  'but',
  'for',
  'i',
  'it',
  'so',
  'the',
  'to',
]);

const variantFor = (value) => {
  if (['founder_clean', 'kinetic_pop', 'proof_impact'].includes(value)) {
    return value;
  }
  return 'founder_clean';
};

const pageTypography = (page, styleConfig, fittedFontSize, maxBoxWidth, displayText) => {
  const variant = variantFor(styleConfig.captionVariant);
  if (page.stylePreset === 'impact_word') {
    const baseSize = styleConfig.fontSize ?? 88;
    const maxImpactSize = styleConfig.impactFontSize ?? (variant === 'proof_impact' ? 112 : baseSize * 2);
    return {
      fontSize: Math.min(maxImpactSize, Math.max(baseSize * 1.45, fittedFontSize * 0.92)),
      lineHeight: styleConfig.lineHeight ?? 0.88,
      columnGap: '0',
      rowGap: 0,
      wordGap: styleConfig.impactWordGap ?? '0.14em',
      padding: '8px 10px',
    };
  }

  if (styleConfig.oneLineBias) {
    const baseSize = styleConfig.fontSize ?? 88;
    const minSize = styleConfig.minFontSize ?? 30;
    const oneLineMaxChars = styleConfig.oneLineMaxChars ?? 26;
    const oneLine = displayText.length <= oneLineMaxChars;
    const charWidth = styleConfig.oneLineCharWidth ?? 0.56;
    const estimatedOneLineSize = maxBoxWidth / Math.max(1, displayText.length * charWidth);
    return {
      fontSize: Math.max(minSize, Math.min(
        baseSize,
        oneLine ? estimatedOneLineSize : fittedFontSize * 0.98,
        fittedFontSize * 0.98,
      )),
      lineHeight: styleConfig.lineHeight ?? 0.94,
      columnGap: '0',
      rowGap: '0.03em',
      wordGap: styleConfig.wordGap ?? '0.18em',
      padding: (styleConfig.boxAlpha ?? 0) > 0 ? '12px 18px 14px' : '8px 10px',
      flexWrap: oneLine ? 'nowrap' : 'wrap',
      whiteSpace: oneLine ? 'nowrap' : undefined,
    };
  }

  if (variant === 'kinetic_pop') {
    return {
      fontSize: Math.min(styleConfig.fontSize ?? 88, Math.max(54, fittedFontSize * 1.32)),
      lineHeight: styleConfig.lineHeight ?? 0.96,
      columnGap: '0',
      rowGap: '0.04em',
      wordGap: styleConfig.wordGap ?? '0.38em',
      padding: (styleConfig.boxAlpha ?? 0) > 0 ? '12px 18px 14px' : '8px 10px',
    };
  }

  return {
    fontSize: Math.min(styleConfig.fontSize ?? 88, Math.max(58, fittedFontSize * 1.22)),
    lineHeight: styleConfig.lineHeight ?? 1.02,
    columnGap: '0',
    rowGap: '0.05em',
    wordGap: styleConfig.wordGap ?? '0.30em',
    padding: (styleConfig.boxAlpha ?? 0) > 0 ? '14px 20px 16px' : '8px 10px',
  };
};

const CaptionPage = ({page, styleConfig, safeZone}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const absoluteSeconds = page.start + frame / fps;
  const isImpact = page.stylePreset === 'impact_word';
  const variant = variantFor(styleConfig.captionVariant);
  const pageFontFamily = isImpact
    ? (styleConfig.impactFontFamily || (variant === 'proof_impact' ? handwrittenFontFamily : styleConfig.fontFamily) || displayFontFamily)
    : (styleConfig.fontFamily || defaultFontFamily);
  const enterFrames = styleConfig.pageEnterFrames ?? 6;
  const enter = interpolate(frame, [0, enterFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const enterSpring = spring({
    frame,
    fps,
    config: isImpact
      ? {damping: 8, stiffness: 260, mass: 0.55}
      : variant === 'kinetic_pop'
        ? {damping: 10, stiffness: 230, mass: 0.55}
        : {damping: 18, stiffness: 140, mass: 0.9},
  });
  const exitFrames = isImpact ? (styleConfig.impactExitFrames ?? 12) : 4;
  const exit = interpolate(
    frame,
    [Math.max(0, (page.end - page.start) * fps - exitFrames), Math.max(1, (page.end - page.start) * fps)],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const opacity = clamp(enter * exit, 0, 1);
  const displayText = page.words.map((word) => word.display || word.text).join(' ');
  const normalizedDisplayText = displayText.toLowerCase().replace(/[^a-z0-9]/g, '');
  const isBlackImpact = isImpact && normalizedDisplayText.includes('black');
  const maxBoxWidth = isImpact
    ? Math.round(width * (styleConfig.impactMaxWidthPercent ?? 0.64))
    : styleConfig.captionMaxWidthPercent
      ? Math.round(width * styleConfig.captionMaxWidthPercent)
      : Math.round(width * (1 - (safeZone?.left ?? 0.08) - (safeZone?.right ?? 0.08)));
  const fitted = fitText({
    fontFamily: pageFontFamily,
    fontWeight: styleConfig.fontWeight ?? 800,
    text: displayText,
    withinWidth: maxBoxWidth,
    textTransform: styleConfig.uppercase ? 'uppercase' : 'none',
  });
  const typography = pageTypography(page, styleConfig, fitted.fontSize, maxBoxWidth, displayText);
  const activeScale = styleConfig.activeScale ?? 1.06;
  const boxAlpha = styleConfig.boxAlpha ?? 0;
  const backColor = withAlpha(styleConfig.backColor, boxAlpha);
  const pageScale = isImpact
    ? clamp(interpolate(enterSpring, [0, 1], [0.72, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'extend',
      }), 0.72, 1.18)
    : variant === 'kinetic_pop'
      ? clamp(interpolate(enterSpring, [0, 1], [0.88, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'extend',
        }), 0.88, 1.10)
      : 1;
  const pageTranslateY = variant === 'kinetic_pop' && !isImpact
    ? interpolate(enterSpring, [0, 1], [18, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : isImpact
      ? interpolate(enterSpring, [0, 1], [-24, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })
      : 0;
  const softShadow = (isBlackImpact ? [
    '0 1px 0 rgba(255, 255, 255, 0.92)',
    '0 7px 11px rgba(0, 0, 0, 0.30)',
    '0 0 18px rgba(255, 255, 255, 0.40)',
  ] : isImpact && variant === 'proof_impact' ? [
    '0 3px 0 rgba(0, 0, 0, 0.75)',
    '0 9px 16px rgba(0, 0, 0, 0.55)',
    '0 0 22px rgba(0, 0, 0, 0.42)',
  ] : [
    '0 2px 2px rgba(0, 0, 0, 0.92)',
    '0 5px 10px rgba(0, 0, 0, 0.74)',
    '0 0 16px rgba(0, 0, 0, 0.62)',
    '0 0 30px rgba(0, 0, 0, 0.42)',
  ]).join(', ');
  const strokeWidth = isImpact
    ? (styleConfig.impactStrokeWidth ?? (variant === 'proof_impact' ? 1.35 : 2.4))
    : styleConfig.strokeWidth >= 0
      ? styleConfig.strokeWidth
      : variant === 'kinetic_pop'
        ? 1.8
        : 0;
  const strokeColor = isImpact
    ? (isBlackImpact
        ? (styleConfig.blackImpactStrokeColor || '#FFFFFF')
        : (styleConfig.impactStrokeColor || '#0A0A0A'))
    : (styleConfig.strokeColor || '#0A0A0A');
  const impactPageTextColor = isBlackImpact
    ? (styleConfig.blackImpactTextColor || '#050505')
    : (styleConfig.impactTextColor || styleConfig.textColor);
  const variantBackColor = variant === 'kinetic_pop' && boxAlpha <= 0
    ? 'rgba(0, 0, 0, 0.18)'
    : boxAlpha > 0 ? backColor : 'transparent';

  return (
    <div style={laneStyle(page.anchor, safeZone)}>
      <div
        style={{
          opacity,
          transform: `translateY(${pageTranslateY}px) skewX(${isImpact && variant === 'proof_impact' ? -5 : 0}deg) rotate(${isImpact && variant === 'proof_impact' ? -2 : 0}deg) scale(${pageScale})`,
          transformOrigin: 'center',
          maxWidth: maxBoxWidth,
          padding: typography.padding,
          borderRadius: 14,
          background: variantBackColor,
          boxDecorationBreak: 'clone',
          WebkitBoxDecorationBreak: 'clone',
          fontFamily: pageFontFamily,
          fontWeight: isImpact ? (styleConfig.impactFontWeight ?? styleConfig.fontWeight ?? 900) : (styleConfig.fontWeight ?? 800),
          fontSize: typography.fontSize,
          lineHeight: typography.lineHeight,
          letterSpacing: isImpact && variant === 'proof_impact' ? '0.01em' : 0,
          display: 'flex',
          flexWrap: typography.flexWrap ?? 'wrap',
          whiteSpace: typography.whiteSpace,
          justifyContent: 'center',
          alignItems: 'baseline',
          columnGap: typography.columnGap,
          rowGap: typography.rowGap,
          color: isImpact ? impactPageTextColor : styleConfig.textColor,
          textShadow: softShadow,
          WebkitTextStroke: strokeWidth > 0 ? `${strokeWidth}px ${strokeColor}` : undefined,
          paintOrder: strokeWidth > 0 ? 'stroke fill' : undefined,
        }}
      >
        {page.words.map((word, index) => {
          const isActive = word.start <= absoluteSeconds && word.end > absoluteSeconds;
          const isEmphasis = Boolean(word.emphasis);
          const revealWords = styleConfig.wordRevealMode === 'spoken';
          const revealFadeSeconds = (styleConfig.wordRevealFadeFrames ?? 2) / fps;
          const firstWordIsWeak = page.words.length > 1 && weakLeadingWords.has(normalizeWordKey(page.words[0]?.display || page.words[0]?.text));
          const revealStart = firstWordIsWeak && index === 1
            ? page.words[0].start
            : word.start;
          const revealOpacity = revealWords
            ? interpolate(
                absoluteSeconds,
                [revealStart, revealStart + revealFadeSeconds],
                [0, 1],
                {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
              )
            : 1;
          const wordFrame = frame - Math.max(0, Math.floor((word.start - page.start) * fps));
          const activePop = isActive
            ? spring({
                frame: Math.max(0, wordFrame),
                fps,
                config: variant === 'kinetic_pop'
                  ? {damping: 7, stiffness: 360, mass: 0.42}
                  : {damping: 12, stiffness: 210, mass: 0.7},
                durationInFrames: variant === 'kinetic_pop' ? 9 : 7,
              })
            : 0;
          const color = isImpact
            ? impactPageTextColor
            : isActive
            ? styleConfig.activeColor
            : isEmphasis
              ? styleConfig.emphasisColor
              : styleConfig.textColor;
          const scale = isActive
            ? activeScale + (variant === 'kinetic_pop' ? activePop * 0.07 : 0)
            : isEmphasis ? 1.015 : 1;
          const translateY = isActive && variant === 'kinetic_pop'
            ? -7 * activePop
            : 0;
          const uppercase = styleConfig.uppercase || (variant === 'proof_impact' && isImpact);

          return (
            <span
              key={`${word.start}-${index}-${word.display}`}
              style={{
                display: 'inline-block',
                color,
                transform: `translateY(${translateY}px) scale(${scale})`,
                transformOrigin: 'center bottom',
                filter: isActive && isImpact ? 'drop-shadow(0 6px 10px rgba(0, 0, 0, 0.28))' : undefined,
                marginRight: index < page.words.length - 1 ? typography.wordGap : 0,
                opacity: revealOpacity,
              }}
            >
              {normalizeText(word.display || word.text, uppercase)}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export const CaptionedVideo = ({
  videoFileName,
  pages,
  overlays,
  safeZone,
  style,
  captionVariant,
}) => {
  const {fps} = useVideoConfig();
  const styleConfig = {
    ...style,
    captionVariant: variantFor(captionVariant || style?.captionVariant),
    fontFamily: resolveCaptionFontFamily(style?.fontFamily, defaultFontFamily),
    impactFontFamily: resolveCaptionFontFamily(style?.impactFontFamily, style?.fontFamily || handwrittenFontFamily),
  };

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <OffthreadVideo
        src={staticFile(videoFileName)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
      {(styleConfig.videoDimAlpha ?? 0) > 0 ? (
        <AbsoluteFill
          style={{
            backgroundColor: 'black',
            opacity: clamp(styleConfig.videoDimAlpha, 0, 0.85),
            pointerEvents: 'none',
          }}
        />
      ) : null}
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        <SocialOverlayLayer overlays={overlays} />
      </AbsoluteFill>
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        <WorkflowOverlayLayer overlays={overlays} />
      </AbsoluteFill>
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        {(pages ?? []).map((page, index) => {
          const startFrame = Math.max(0, Math.floor(page.start * fps));
          const endFrame = Math.max(startFrame + 1, Math.ceil(page.end * fps));
          return (
            <Sequence
              key={`${page.start}-${index}`}
              from={startFrame}
              durationInFrames={endFrame - startFrame}
            >
              <CaptionPage page={page} styleConfig={styleConfig} safeZone={safeZone} />
            </Sequence>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
