import React from 'react';
import {
  Html5Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {fitText} from '@remotion/layout-utils';
import {defaultFontFamily, displayFontFamily} from './fonts.js';

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const numberOr = (value, fallback) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
};

const cssString = (value) => String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"');

const panelPlacementStyle = (overlay, width, height) => {
  const panelWidth = clamp(numberOr(overlay.width, 780), 320, width - 110);
  const bottom = numberOr(
    overlay.bottom,
    Math.round(height * numberOr(overlay.bottomPercent, 0.28)),
  );
  const sidePad = numberOr(overlay.sidePad, 60);

  if (overlay.anchor === 'lower_left') {
    return {width: panelWidth, left: sidePad, bottom};
  }
  if (overlay.anchor === 'lower_right') {
    return {width: panelWidth, right: sidePad, bottom};
  }
  return {
    width: panelWidth,
    left: (width - panelWidth) / 2,
    bottom,
  };
};

const usePopMotion = (durationInFrames) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({
    frame,
    fps,
    config: {
      damping: 18,
      stiffness: 150,
      mass: 0.82,
    },
  });
  const outStart = Math.max(1, durationInFrames - 10);
  const exit = interpolate(frame, [outStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const opacity = clamp(enter * exit, 0, 1);
  const translateY = interpolate(enter, [0, 1], [88, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = interpolate(enter, [0, 1], [0.95, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return {frame, opacity, transform: `translateY(${translateY}px) scale(${scale})`};
};

const ClaudeMark = ({size = 48}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: 14,
      background: '#D97858',
      position: 'relative',
      flex: '0 0 auto',
      boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.35), 0 12px 24px rgba(101, 55, 36, 0.20)',
    }}
  >
    {[0, 1, 2, 3].map((index) => (
      <div
        key={index}
        style={{
          position: 'absolute',
          left: size * 0.5 - size * 0.055,
          top: size * 0.18,
          width: size * 0.11,
          height: size * 0.64,
          borderRadius: 999,
          background: 'rgba(255, 247, 235, 0.92)',
          transform: `rotate(${index * 45}deg)`,
          transformOrigin: `50% ${size * 0.32}px`,
        }}
      />
    ))}
  </div>
);

const SendArrow = ({size = 28}) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
    <path
      d="M7 17 25 7l-6 18-4-7-8-1z"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="m15 18 10-11"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
    />
  </svg>
);

const ClaudeSpinner = ({size = 28, rotation = 0, opacity = 1, scale = 1}) => (
  <div
    style={{
      width: size,
      height: size,
      position: 'absolute',
      opacity,
      transform: `rotate(${rotation}deg) scale(${scale})`,
    }}
  >
    {[0, 1, 2, 3].map((index) => (
      <div
        key={index}
        style={{
          position: 'absolute',
          left: size * 0.5 - size * 0.055,
          top: size * 0.17,
          width: size * 0.11,
          height: size * 0.66,
          borderRadius: 999,
          background: '#FFFFFF',
          transform: `rotate(${index * 45}deg)`,
          transformOrigin: `50% ${size * 0.33}px`,
          opacity: 0.94,
        }}
      />
    ))}
  </div>
);

export const ClaudePromptModal = ({overlay, durationInFrames}) => {
  const {width, height} = useVideoConfig();
  const {frame, opacity, transform} = usePopMotion(durationInFrames);
  const data = {
    title: 'Claude',
    subtitle: 'Desktop',
    greeting: '',
    placeholder: 'How can I help you?',
    ask: 'help me edit my video',
    status: 'New chat',
    typingSound: null,
    typingTrack: null,
    typingVolume: 0.08,
    ...overlay,
  };
  const placement = panelPlacementStyle(data, width, height);
  const visualScale = numberOr(data.scale, 1);
  const typeStart = numberOr(data.typeStartFrame, 8);
  const framesPerChar = numberOr(data.typeFramesPerChar, 1.75);
  const typeEnd = Math.min(
    Math.max(typeStart + 1, typeStart + data.ask.length * framesPerChar),
    Math.max(typeStart + 1, durationInFrames - 14),
  );
  const chars = Math.floor(interpolate(frame, [typeStart, typeEnd], [0, data.ask.length], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));
  const typed = data.ask.slice(0, chars);
  const caretVisible = chars > 0 && Math.floor(frame / 8) % 2 === 0 && chars < data.ask.length;
  const hasGreeting = Boolean(data.greeting);
  const doneTyping = chars >= data.ask.length;
  const submitStart = Math.round(numberOr(data.submitStartFrame, typeEnd + 8));
  const loadingStart = submitStart + 7;
  const pressScale = interpolate(frame, [submitStart, submitStart + 3, submitStart + 8], [1.03, 0.78, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const loading = interpolate(frame, [loadingStart, loadingStart + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const buttonScale = frame >= submitStart ? pressScale : doneTyping ? 1.03 : 1;
  const arrowOpacity = 1 - loading;
  const arrowShift = interpolate(loading, [0, 1], [0, -7], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const spinnerRotation = frame >= loadingStart ? (frame - loadingStart) * 13 : 0;
  const spinnerScale = interpolate(loading, [0, 1], [0.62, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        ...placement,
        opacity,
        transform: `${transform} scale(${visualScale})`,
        transformOrigin: 'center bottom',
        fontFamily: data.fontFamily || defaultFontFamily,
        filter: 'drop-shadow(0 30px 46px rgba(0, 0, 0, 0.34))',
      }}
    >
      <div
        style={{
          borderRadius: 30,
          background: '#F7F3EA',
          color: '#141413',
          border: '1px solid rgba(31, 30, 29, 0.14)',
          overflow: 'hidden',
          boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.9)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            padding: '22px 24px 14px',
          }}
        >
          <ClaudeMark size={48} />
          <div style={{flex: 1}}>
            <div style={{fontSize: 28, lineHeight: 1, fontWeight: 850, letterSpacing: 0}}>
              {data.title}
            </div>
            <div style={{fontSize: 17, lineHeight: 1.2, color: '#73726C', fontWeight: 700, marginTop: 5}}>
              {data.subtitle}
            </div>
          </div>
          <div
            style={{
              borderRadius: 999,
              padding: '8px 12px',
              background: '#E8E2D6',
              color: '#5A564F',
              fontSize: 15,
              fontWeight: 800,
            }}
          >
            {data.status}
          </div>
        </div>

        <div style={{padding: hasGreeting ? '8px 28px 24px' : '12px 28px 24px'}}>
          {hasGreeting ? (
            <div
              style={{
                fontSize: 34,
                lineHeight: 1.04,
                fontWeight: 780,
                letterSpacing: 0,
                color: '#403D38',
                marginBottom: 17,
              }}
            >
              {data.greeting}
            </div>
          ) : null}
          <div
            style={{
              minHeight: 82,
              borderRadius: 22,
              background: '#FFFFFF',
              border: '1px solid rgba(31, 30, 29, 0.12)',
              display: 'flex',
              alignItems: 'center',
              gap: 14,
              padding: '0 14px 0 22px',
              boxShadow: '0 14px 30px rgba(52, 45, 38, 0.08)',
            }}
          >
            <div
              style={{
                flex: 1,
                fontSize: 34,
                lineHeight: 1,
                color: typed ? '#141413' : '#B9B4AA',
                fontWeight: typed ? 820 : 560,
                letterSpacing: 0,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
              }}
            >
              {typed || data.placeholder}
              {caretVisible ? <span style={{color: '#D97858'}}> |</span> : null}
            </div>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 16,
                background: doneTyping ? '#D97858' : '#E8E2D6',
                color: doneTyping ? '#FFFFFF' : '#73726C',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                transform: `scale(${buttonScale})`,
                boxShadow: frame >= submitStart
                  ? 'inset 0 3px 8px rgba(94, 45, 26, 0.26)'
                  : doneTyping
                    ? '0 10px 18px rgba(217, 120, 88, 0.25)'
                    : 'none',
              }}
            >
              <div
                style={{
                  opacity: arrowOpacity,
                  transform: `translate(${arrowShift}px, ${arrowShift}px) scale(${1 - loading * 0.18})`,
                }}
              >
                <SendArrow size={25} />
              </div>
              <ClaudeSpinner
                size={27}
                rotation={spinnerRotation}
                opacity={loading}
                scale={spinnerScale}
              />
            </div>
          </div>
        </div>
      </div>
      {data.typingTrack ? (
        <Sequence
          from={Math.round(typeStart)}
          durationInFrames={Math.max(1, Math.ceil(typeEnd - typeStart + 12))}
        >
          <Html5Audio
            src={staticFile(data.typingTrack)}
            volume={numberOr(data.typingVolume, 0.08)}
          />
        </Sequence>
      ) : data.typingSound ? (
        <>
          {Array.from({length: data.ask.length}).map((_, index) => (
            <Sequence
              key={`typing-${index}`}
              from={Math.round(typeStart + index * framesPerChar)}
              durationInFrames={5}
            >
              <Html5Audio
                src={staticFile(data.typingSound)}
                volume={numberOr(data.typingVolume, 0.08)}
              />
            </Sequence>
          ))}
        </>
      ) : null}
    </div>
  );
};

const FfmpegMark = ({size = 44}) => (
  <svg width={size} height={size} viewBox="0 0 44 44" fill="none">
    <rect x="3" y="3" width="38" height="38" rx="11" fill="#142113" />
    <path
      d="M11 26 18 18l6 6 9-11"
      stroke="#85D46A"
      strokeWidth="4"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M12 32h20"
      stroke="#E8F6E2"
      strokeWidth="3"
      strokeLinecap="round"
      opacity="0.9"
    />
  </svg>
);

const FilmFrame = ({index, src}) => {
  return (
    <div
      style={{
        width: 84,
        height: 62,
        borderRadius: 8,
        border: '3px solid #D7D7D0',
        background: 'linear-gradient(135deg, #2A2B27, #111210)',
        position: 'relative',
        overflow: 'hidden',
        flex: '0 0 auto',
      }}
    >
      {src ? (
        <Img
          src={staticFile(src)}
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'saturate(0.9) contrast(1.05)',
          }}
        />
      ) : (
        <div
          style={{
            position: 'absolute',
            inset: '7px 8px',
            borderRadius: 5,
            background: `linear-gradient(135deg, rgba(255,255,255,${0.12 + index * 0.012}), rgba(255,255,255,0.02))`,
          }}
        />
      )}
      <div style={{position: 'absolute', inset: 0, background: 'rgba(0, 0, 0, 0.18)'}} />
      {[9, 26, 43].map((top) => (
        <React.Fragment key={top}>
          <div style={{position: 'absolute', left: 3, top, width: 7, height: 5, borderRadius: 2, background: '#0D0E0C'}} />
          <div style={{position: 'absolute', right: 3, top, width: 7, height: 5, borderRadius: 2, background: '#0D0E0C'}} />
        </React.Fragment>
      ))}
    </div>
  );
};

export const FfmpegCutModal = ({overlay, durationInFrames}) => {
  const {width, height} = useVideoConfig();
  const {frame, opacity, transform} = usePopMotion(durationInFrames);
  const data = {
    title: 'ffmpeg',
    subtitle: 'cutting video',
    command: 'ffmpeg -i raw.mov -ss 00:12 -to 00:18 -c copy clip.mp4',
    ...overlay,
  };
  const placement = panelPlacementStyle({...data, width: numberOr(data.width, 820), bottomPercent: numberOr(data.bottomPercent, 0.23)}, width, height);
  const visualScale = numberOr(data.scale, 1);
  const progress = interpolate(frame, [8, Math.min(durationInFrames - 10, 72)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cutOne = interpolate(frame, [10, 15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cutTwo = interpolate(frame, [18, 23], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const removeMiddle = interpolate(frame, [25, 36], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const closeGap = interpolate(frame, [34, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cutFade = interpolate(frame, [48, 62], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const frameSources = Array.isArray(data.frames) ? data.frames : [];
  const frameWidth = 84;
  const gap = 10;
  const leftCount = 3;
  const middleCount = 2;
  const middleShift = middleCount * (frameWidth + gap);
  const cutOneX = 16 + leftCount * (frameWidth + gap) - gap / 2;
  const cutTwoX = 16 + (leftCount + middleCount) * (frameWidth + gap) - gap / 2;
  const logs = [
    'input: raw/day_02/selfie_take_01.mov',
    'detecting edit window...',
    'cut: 00:12.00 -> 00:18.00',
    'writing: edits/day_02/clip_01.mp4',
  ];
  const cutSoundFrames = Array.isArray(data.cutSoundFrames)
    ? data.cutSoundFrames.map((value) => Math.round(numberOr(value, 0)))
    : [10, 18];
  const visibleLogs = Math.min(logs.length, Math.floor(interpolate(frame, [10, durationInFrames - 18], [1, logs.length + 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  })));

  return (
    <div
      style={{
        position: 'absolute',
        ...placement,
        opacity,
        transform: `${transform} scale(${visualScale})`,
        transformOrigin: 'center bottom',
        fontFamily: data.fontFamily || defaultFontFamily,
        filter: 'drop-shadow(0 30px 48px rgba(0, 0, 0, 0.36))',
      }}
    >
      <div
        style={{
          borderRadius: 28,
          background: '#10120F',
          color: '#F4F4EA',
          border: '1px solid rgba(218, 255, 196, 0.14)',
          overflow: 'hidden',
          boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            padding: '22px 24px 16px',
            borderBottom: '1px solid rgba(255,255,255,0.08)',
          }}
        >
          <FfmpegMark size={46} />
          <div style={{flex: 1}}>
            <div style={{fontSize: 29, lineHeight: 1, fontWeight: 900, letterSpacing: 0}}>
              {data.title}
            </div>
            <div style={{fontSize: 16, lineHeight: 1.2, color: '#9DAA95', fontWeight: 750, marginTop: 6}}>
              {data.subtitle}
            </div>
          </div>
          <div
            style={{
              borderRadius: 999,
              padding: '8px 13px',
              background: 'rgba(133, 212, 106, 0.14)',
              color: '#9BE279',
              fontSize: 15,
              fontWeight: 900,
            }}
          >
            {Math.round(progress * 100)}%
          </div>
        </div>

        <div style={{padding: '18px 24px 24px'}}>
          <div
            style={{
              fontFamily: 'Menlo, Consolas, monospace',
              fontSize: 17,
              lineHeight: 1.35,
              color: '#DDEBD6',
              background: 'rgba(0,0,0,0.30)',
              borderRadius: 16,
              padding: '15px 17px',
              border: '1px solid rgba(255,255,255,0.07)',
              marginBottom: 18,
            }}
          >
            <div style={{color: '#85D46A'}}>$ {data.command}</div>
            {logs.slice(0, visibleLogs).map((log) => (
              <div key={log} style={{color: '#AEB8A8', marginTop: 5}}>
                {log}
              </div>
            ))}
          </div>

          <div
            style={{
              position: 'relative',
              overflow: 'hidden',
              borderRadius: 18,
              background: '#070807',
              padding: '18px 16px',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <div
              style={{
                display: 'flex',
                gap,
                transform: `translateX(${interpolate(progress, [0, 1], [0, -8])}px)`,
                alignItems: 'center',
              }}
            >
              <div style={{display: 'flex', gap}}>
                {Array.from({length: leftCount}).map((_, index) => (
                  <FilmFrame key={`left-${index}`} index={index} src={frameSources[index]} />
                ))}
              </div>
              <div
                style={{
                  display: 'flex',
                  gap,
                  opacity: interpolate(removeMiddle, [0, 1], [1, 0], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  }),
                  transform: `translateY(${interpolate(removeMiddle, [0, 1], [0, 46])}px) scale(${interpolate(removeMiddle, [0, 1], [1, 0.92])})`,
                  filter: `blur(${interpolate(removeMiddle, [0, 1], [0, 1.4])}px)`,
                }}
              >
                {Array.from({length: middleCount}).map((_, index) => {
                  const sourceIndex = leftCount + index;
                  return (
                    <FilmFrame
                      key={`middle-${index}`}
                      index={sourceIndex}
                      src={frameSources[sourceIndex]}
                    />
                  );
                })}
              </div>
              <div
                style={{
                  display: 'flex',
                  gap,
                  transform: `translateX(${-middleShift * closeGap}px)`,
                }}
              >
                {Array.from({length: 3}).map((_, index) => {
                  const sourceIndex = leftCount + middleCount + index;
                  return (
                    <FilmFrame
                      key={`right-${index}`}
                      index={sourceIndex}
                      src={frameSources[sourceIndex]}
                    />
                  );
                })}
              </div>
            </div>
            <div
              style={{
                position: 'absolute',
                left: cutOneX,
                top: 10,
                bottom: 10,
                width: 4,
                borderRadius: 999,
                background: '#FF5A4F',
                boxShadow: '0 0 18px rgba(255, 90, 79, 0.70)',
                opacity: cutOne * cutFade,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: cutTwoX,
                top: 10,
                bottom: 10,
                width: 4,
                borderRadius: 999,
                background: '#FF5A4F',
                boxShadow: '0 0 18px rgba(255, 90, 79, 0.70)',
                opacity: cutTwo * cutFade,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: cutOne < 1 ? Math.max(16, cutOneX - 28) : Math.max(16, cutTwoX - 28),
                top: 8,
                borderRadius: 999,
                padding: '5px 9px',
                background: '#FF5A4F',
                color: '#FFFFFF',
                fontSize: 12,
                fontWeight: 950,
                letterSpacing: 0,
                opacity: Math.max(cutOne, cutTwo) * cutFade,
              }}
            >
              CUT
            </div>
          </div>
        </div>
      </div>
      {data.cutSound ? (
        <>
          {cutSoundFrames.map((startFrame, index) => (
            startFrame >= 0 && startFrame < durationInFrames ? (
              <Sequence
                key={`ffmpeg-cut-sound-${index}-${startFrame}`}
                from={startFrame}
                durationInFrames={Math.max(1, durationInFrames - startFrame)}
              >
                <Html5Audio
                  src={staticFile(data.cutSound)}
                  volume={numberOr(data.cutSoundVolume, 0.48)}
                />
              </Sequence>
            ) : null
          ))}
        </>
      ) : null}
    </div>
  );
};

export const SlamTitleOverlay = ({overlay, durationInFrames}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const data = {
    text: 'DAY TWO',
    color: '#FFFFFF',
    accentColor: '#FF5A4F',
    edgeColor: 'rgba(0, 0, 0, 0.34)',
    shadowColor: 'rgba(0, 0, 0, 0.42)',
    slamSound: null,
    slamVolume: 0.8,
    topPercent: 0.035,
    widthPercent: 0.92,
    fontSize: 270,
    accentLastWord: true,
    ...overlay,
  };
  const top = numberOr(data.top, Math.round(height * numberOr(data.topPercent, 0.035)));
  const maxWidth = Math.round(width * numberOr(data.widthPercent, 0.92));
  const titleText = String(data.text).toUpperCase();
  const fontFamily = data.fontFamily || displayFontFamily;
  const fontWeight = numberOr(data.fontWeight, 400);
  const fontFormat = data.fontFormat || 'truetype';
  const requestedFontSize = numberOr(data.fontSize, 270);
  const fittedFontSize = fitText({
    text: titleText,
    withinWidth: maxWidth,
    fontFamily,
    fontWeight,
    letterSpacing: '0px',
    textTransform: 'uppercase',
    validateFontIsLoaded: false,
  }).fontSize;
  const titleFontSize = Math.min(requestedFontSize, fittedFontSize * 0.95);
  const exitStart = Math.max(1, durationInFrames - 8);
  const enter = spring({
    frame,
    fps,
    config: {
      damping: 8,
      stiffness: 245,
      mass: 0.54,
    },
  });
  const exit = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const hit = clamp(enter, 0, 1);
  const opacity = clamp(hit * exit, 0, 1);
  const y = interpolate(hit, [0, 0.82, 1], [-720, 22, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const baseScale = interpolate(hit, [0, 0.72, 1], [1.45, 1.08, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const rotation = interpolate(hit, [0, 1], [-6, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const squash = interpolate(frame, [4, 7, 13], [1, 0.84, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const stretch = interpolate(frame, [4, 7, 13], [1.08, 0.92, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const settle = interpolate(frame, [7, 20], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shake = Math.sin(frame * 2.9) * 8 * settle;
  const impactGlow = interpolate(frame, [5, 8, 18], [0, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const words = String(data.text).split(/\s+/).filter(Boolean);

  return (
    <>
      {data.fontFile ? (
        <style>
          {`@font-face {
  font-family: "${cssString(fontFamily)}";
  src: url("${staticFile(data.fontFile)}") format("${cssString(fontFormat)}");
  font-weight: ${fontWeight};
  font-style: normal;
  font-display: block;
}`}
        </style>
      ) : null}
      <div
        style={{
          position: 'absolute',
          top,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          opacity,
          transform: `translate(${shake}px, ${y}px) rotate(${rotation}deg) scale(${baseScale * stretch}, ${baseScale * squash})`,
          transformOrigin: 'center top',
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            position: 'relative',
            maxWidth,
            textAlign: 'center',
            fontFamily,
            fontSize: titleFontSize,
            lineHeight: 0.78,
            fontWeight,
            letterSpacing: 0,
            textTransform: 'uppercase',
            color: data.color,
            WebkitTextStroke: `${numberOr(data.strokeWidth, 1.4)}px ${data.edgeColor}`,
            textShadow: [
              `0 3px 4px ${data.shadowColor}`,
              '0 12px 24px rgba(0, 0, 0, 0.38)',
              '0 24px 48px rgba(0, 0, 0, 0.26)',
              '0 0 20px rgba(0, 0, 0, 0.22)',
            ].join(', '),
            whiteSpace: 'nowrap',
          }}
        >
          <div
            style={{
              position: 'absolute',
              inset: 0,
              color: data.accentColor,
              opacity: impactGlow * 0.65,
              transform: `translate(${interpolate(impactGlow, [0, 1], [0, 14])}px, ${interpolate(impactGlow, [0, 1], [0, 10])}px)`,
              filter: 'blur(1px)',
              zIndex: -1,
            }}
          >
            {titleText}
          </div>
          {words.map((word, index) => {
            const isAccent = Boolean(data.accentLastWord) && index === words.length - 1;
            return (
              <span
                key={`${word}-${index}`}
                style={{
                  color: isAccent ? data.accentColor : data.color,
                  display: 'inline-block',
                  marginLeft: index === 0 ? 0 : '0.08em',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
        {data.slamSound ? (
          <Sequence
            from={Math.max(0, Math.round(numberOr(data.soundOffsetFrame, 0)))}
            durationInFrames={Math.max(1, durationInFrames)}
          >
            <Html5Audio
              src={staticFile(data.slamSound)}
              volume={numberOr(data.slamVolume, 0.8)}
            />
          </Sequence>
        ) : null}
      </div>
    </>
  );
};

export const WorkflowOverlayLayer = ({overlays}) => {
  const {fps} = useVideoConfig();
  const workflowTypes = ['claude_prompt_modal', 'ffmpeg_cut_modal', 'slam_title'];

  return (
    <>
      {(overlays ?? []).map((overlay, index) => {
        if (!workflowTypes.includes(overlay.type)) {
          return null;
        }
        const startSeconds = numberOr(overlay.start, 0);
        const endSeconds = numberOr(overlay.end, startSeconds + numberOr(overlay.duration, 4));
        const startFrame = Math.max(0, Math.floor(startSeconds * fps));
        const endFrame = Math.max(startFrame + 1, Math.ceil(endSeconds * fps));
        return (
          <Sequence
            key={`${overlay.type}-${overlay.start}-${index}`}
            from={startFrame}
            durationInFrames={endFrame - startFrame}
          >
            {overlay.type === 'claude_prompt_modal' ? (
              <ClaudePromptModal overlay={overlay} durationInFrames={endFrame - startFrame} />
            ) : overlay.type === 'ffmpeg_cut_modal' ? (
              <FfmpegCutModal overlay={overlay} durationInFrames={endFrame - startFrame} />
            ) : (
              <SlamTitleOverlay overlay={overlay} durationInFrames={endFrame - startFrame} />
            )}
          </Sequence>
        );
      })}
    </>
  );
};
