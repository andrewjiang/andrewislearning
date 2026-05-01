import React from 'react';
import {
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {defaultFontFamily} from './fonts.js';

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const numberOr = (value, fallback) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
};

const normalizeOverlay = (overlay) => ({
  type: 'instagram_float',
  headline: 'Reposted on Instagram',
  subhead: 'Someone took the clip and got the conversation.',
  handle: '@andrewislearning',
  source: 'Instagram',
  metric: '2,000+ comments',
  note: 'demo link in comments',
  accent: '#FF5A4F',
  anchor: 'lower_center',
  ...overlay,
});

const InstagramGlyph = ({accent}) => (
  <div
    style={{
      width: 58,
      height: 58,
      borderRadius: 17,
      background: `linear-gradient(135deg, #5B4DFF 0%, ${accent} 48%, #FFD36B 100%)`,
      boxShadow: `0 10px 26px rgba(255, 90, 79, 0.35)`,
      position: 'relative',
      flex: '0 0 auto',
    }}
  >
    <div
      style={{
        position: 'absolute',
        inset: 12,
        border: '4px solid rgba(255, 255, 255, 0.92)',
        borderRadius: 12,
      }}
    />
    <div
      style={{
        position: 'absolute',
        left: 22,
        top: 22,
        width: 14,
        height: 14,
        border: '4px solid rgba(255, 255, 255, 0.92)',
        borderRadius: 999,
      }}
    />
    <div
      style={{
        position: 'absolute',
        right: 16,
        top: 16,
        width: 7,
        height: 7,
        borderRadius: 999,
        background: 'rgba(255, 255, 255, 0.95)',
      }}
    />
  </div>
);

const SvgIcon = ({children, size = 40, stroke = 'currentColor', fill = 'none', style}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 48 48"
    fill={fill}
    stroke={stroke}
    strokeWidth="3.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    style={{display: 'block', ...style}}
  >
    {children}
  </svg>
);

const HeartIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M24 40s-15-8.8-18.5-19.2C2.7 12.5 11.8 6.6 18.6 12.6L24 18l5.4-5.4c6.8-6 15.9-.1 13.1 8.2C39 31.2 24 40 24 40z" />
  </SvgIcon>
);

const CommentIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M10 12.5c3.5-3.2 8.2-5 14-5 10.2 0 18 6.6 18 15.5 0 8.7-7.6 15.4-17.7 15.4-2.2 0-4.3-.3-6.2-1L8 40l3-8.2C7.8 29.1 6 25.9 6 23c0-4.1 1.3-7.6 4-10.5z" />
  </SvgIcon>
);

const SendIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M6 24 42 7 29 41l-6-13-17-4z" />
    <path d="M23 28 42 7" />
  </SvgIcon>
);

const CameraIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M14 16h20l3 4h5v18H6V20h5l3-4z" />
    <circle cx="24" cy="29" r="7.2" />
    <path d="M33 23h.01" />
  </SvgIcon>
);

const VerifiedBadge = ({size = 22}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: 999,
      background: '#129CFF',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#FFFFFF',
      flex: '0 0 auto',
      filter: 'drop-shadow(0 2px 3px rgba(0, 0, 0, 0.35))',
    }}
  >
    <SvgIcon size={Math.round(size * 0.72)} stroke="#FFFFFF">
      <path d="m14 24 6 6 14-15" />
    </SvgIcon>
  </div>
);

const HomeIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M7 23 24 9l17 14" />
    <path d="M13 22v18h22V22" />
  </SvgIcon>
);

const SearchIcon = (props) => (
  <SvgIcon {...props}>
    <circle cx="21" cy="21" r="12" />
    <path d="m31 31 10 10" />
  </SvgIcon>
);

const PlusIcon = (props) => (
  <SvgIcon {...props}>
    <rect x="10" y="10" width="28" height="28" rx="8" />
    <path d="M24 16v16" />
    <path d="M16 24h16" />
  </SvgIcon>
);

const ReelsIcon = (props) => (
  <SvgIcon {...props}>
    <rect x="9" y="11" width="30" height="27" rx="6" />
    <path d="M9 20h30" />
    <path d="m15 11 6 9" />
    <path d="m28 11 6 9" />
    <path d="m22 27 8 5-8 5z" fill="currentColor" stroke="none" />
  </SvgIcon>
);

const ProfileIcon = (props) => (
  <SvgIcon {...props}>
    <circle cx="24" cy="18" r="7" />
    <path d="M10 40c2.2-8 7-12 14-12s11.8 4 14 12" />
  </SvgIcon>
);

const MusicIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M18 34V12l20-4v22" />
    <circle cx="13" cy="35" r="5" />
    <circle cx="33" cy="31" r="5" />
  </SvgIcon>
);

const MoreIcon = ({size = 40, color = 'currentColor'}) => (
  <div
    style={{
      width: size,
      height: size,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 4,
      color,
    }}
  >
    {[0, 1, 2].map((item) => (
      <span
        key={item}
        style={{
          width: 5,
          height: 5,
          borderRadius: 999,
          background: 'currentColor',
          display: 'block',
        }}
      />
    ))}
  </div>
);

const AvatarImage = ({src, size = 44, style}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: 999,
      background: '#F7F7F7',
      border: '2px solid rgba(255, 255, 255, 0.92)',
      boxShadow: '0 8px 18px rgba(0, 0, 0, 0.35)',
      overflow: 'hidden',
      flex: '0 0 auto',
      ...style,
    }}
  >
    {src ? (
      <Img
        src={staticFile(src)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block',
        }}
      />
    ) : null}
  </div>
);

const placementStyle = (overlay, width, height) => {
  const cardWidth = clamp(numberOr(overlay.width, 780), 560, width - 120);
  const bottom = numberOr(
    overlay.bottom,
    Math.round(height * numberOr(overlay.bottomPercent, 0.30)),
  );
  const sidePad = numberOr(overlay.sidePad, 76);

  if (overlay.anchor === 'lower_left') {
    return {width: cardWidth, left: sidePad, bottom};
  }
  if (overlay.anchor === 'lower_right') {
    return {width: cardWidth, right: sidePad, bottom};
  }
  return {
    width: cardWidth,
    left: (width - cardWidth) / 2,
    bottom,
  };
};

const reelPlacementStyle = (overlay, width, height) => {
  const reelWidth = clamp(numberOr(overlay.width, 500), 200, width - 110);
  const reelHeight = clamp(numberOr(overlay.height, Math.round(reelWidth * 1.82)), 320, height - 140);
  const bottom = numberOr(
    overlay.bottom,
    Math.round(height * numberOr(overlay.bottomPercent, 0.08)),
  );
  const sidePad = numberOr(overlay.sidePad, 52);

  if (overlay.anchor === 'lower_left') {
    return {width: reelWidth, height: reelHeight, left: sidePad, bottom};
  }
  if (overlay.anchor === 'lower_right') {
    return {width: reelWidth, height: reelHeight, right: sidePad, bottom};
  }
  return {
    width: reelWidth,
    height: reelHeight,
    left: (width - reelWidth) / 2,
    bottom,
  };
};

export const FloatingInstagramOverlay = ({overlay, durationInFrames}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const data = normalizeOverlay(overlay);
  const accent = data.accent || '#FF5A4F';
  const enter = spring({
    frame,
    fps,
    config: {
      damping: 18,
      stiffness: 150,
      mass: 0.8,
    },
  });
  const outStart = Math.max(1, durationInFrames - 9);
  const exit = interpolate(frame, [outStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const drift = interpolate(frame, [0, durationInFrames], [0, -36], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const opacity = clamp(enter * exit, 0, 1);
  const translateY = interpolate(enter, [0, 1], [160, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }) + drift;
  const scale = interpolate(enter, [0, 1], [0.94, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const placement = placementStyle(data, width, height);
  const reactions = data.reactions || [
    {label: 'likes', value: '3.5K'},
    {label: 'comments', value: '2,000+'},
    {label: 'shares', value: '80'},
  ];

  return (
    <div
      style={{
        position: 'absolute',
        ...placement,
        opacity,
        transform: `translateY(${translateY}px) scale(${scale})`,
        transformOrigin: 'center bottom',
        fontFamily: data.fontFamily || defaultFontFamily,
        color: '#111111',
        filter: 'drop-shadow(0 28px 42px rgba(0, 0, 0, 0.35))',
      }}
    >
      <div
        style={{
          borderRadius: 34,
          background: 'rgba(255, 255, 255, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.72)',
          overflow: 'hidden',
          boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(20px)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 18,
            padding: '26px 30px 20px',
          }}
        >
          <InstagramGlyph accent={accent} />
          <div style={{minWidth: 0, flex: 1}}>
            <div
              style={{
                fontSize: 30,
                lineHeight: 1,
                fontWeight: 900,
                letterSpacing: 0,
              }}
            >
              {data.source}
            </div>
            <div
              style={{
                marginTop: 7,
                fontSize: 20,
                lineHeight: 1.05,
                color: 'rgba(17, 17, 17, 0.58)',
                fontWeight: 800,
              }}
            >
              {data.handle}
            </div>
          </div>
          <div
            style={{
              borderRadius: 999,
              background: 'rgba(255, 90, 79, 0.12)',
              color: accent,
              padding: '12px 17px',
              fontSize: 18,
              lineHeight: 1,
              fontWeight: 900,
              whiteSpace: 'nowrap',
            }}
          >
            {data.metric}
          </div>
        </div>

        <div style={{padding: '0 30px 26px'}}>
          <div
            style={{
              fontSize: Number(data.headlineSize ?? 42),
              lineHeight: 1.02,
              fontWeight: 900,
              letterSpacing: 0,
            }}
          >
            {data.headline}
          </div>
          <div
            style={{
              marginTop: 12,
              fontSize: 24,
              lineHeight: 1.18,
              color: 'rgba(17, 17, 17, 0.66)',
              fontWeight: 800,
            }}
          >
            {data.subhead}
          </div>
        </div>

        <div
          style={{
            height: 1,
            background: 'rgba(17, 17, 17, 0.08)',
          }}
        />

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '18px 30px 22px',
          }}
        >
          <div style={{display: 'flex', gap: 12}}>
            {reactions.map((reaction, index) => (
              <div
                key={`${reaction.label}-${index}`}
                style={{
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: 6,
                  borderRadius: 999,
                  background: 'rgba(17, 17, 17, 0.06)',
                  padding: '10px 12px',
                }}
              >
                <span style={{fontSize: 19, fontWeight: 900}}>{reaction.value}</span>
                <span
                  style={{
                    fontSize: 15,
                    fontWeight: 800,
                    color: 'rgba(17, 17, 17, 0.52)',
                  }}
                >
                  {reaction.label}
                </span>
              </div>
            ))}
          </div>
          <div
            style={{
              fontSize: 17,
              fontWeight: 900,
              color: 'rgba(17, 17, 17, 0.48)',
              maxWidth: 190,
              textAlign: 'right',
              lineHeight: 1.05,
            }}
          >
            {data.note}
          </div>
        </div>
      </div>
    </div>
  );
};

const ReelAction = ({icon, label}) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 5,
      color: '#FFFFFF',
      textShadow: '0 3px 8px rgba(0, 0, 0, 0.88)',
      fontWeight: 850,
    }}
  >
    {icon}
    {label ? (
      <div style={{fontSize: 18, lineHeight: 1}}>{label}</div>
    ) : null}
  </div>
);

const BottomNavItem = ({children, active}) => (
  <div
    style={{
      color: active ? '#000000' : '#111111',
      opacity: active ? 1 : 0.94,
      transform: active ? 'scale(1.08)' : 'scale(1)',
    }}
  >
    {children}
  </div>
);

export const InstagramReelMockOverlay = ({overlay, durationInFrames}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const data = {
    username: 'andrewislearning',
    audio: 'Original audio',
    caption: 'Day 1 of training AI to be my video editor. Written, edited, captioned, and published by AI. Follow + comment "DAY 1" for the guide + plugin.',
    captionPreview: null,
    likeCount: '0',
    commentCount: '0',
    shareCount: '0',
    videoLabel: '',
    accent: '#FF2D6F',
    avatar: null,
    verified: true,
    ...overlay,
  };
  const enter = spring({
    frame,
    fps,
    config: {
      damping: 19,
      stiffness: 135,
      mass: 0.85,
    },
  });
  const outStart = Math.max(1, durationInFrames - 10);
  const exit = interpolate(frame, [outStart, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const drift = interpolate(frame, [0, durationInFrames], [0, -42], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const opacity = clamp(enter * exit, 0, 1);
  const translateY = interpolate(enter, [0, 1], [220, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }) + drift;
  const finalRotate = numberOr(data.rotation ?? data.rotate, 0);
  const rotate = interpolate(enter, [0, 1], [finalRotate + 2.5, finalRotate], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = interpolate(enter, [0, 1], [0.92, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const placement = reelPlacementStyle(data, width, height);
  const navHeight = Math.round(placement.height * 0.105);
  const screenHeight = placement.height - navHeight;
  const railBottom = Math.round(navHeight + screenHeight * 0.125);
  const previewCaption = data.captionPreview || data.caption;

  return (
    <div
      style={{
        position: 'absolute',
        ...placement,
        opacity,
        transform: `translateY(${translateY}px) rotate(${rotate}deg) scale(${scale})`,
        transformOrigin: 'center bottom',
        filter: 'drop-shadow(0 34px 50px rgba(0, 0, 0, 0.38))',
        fontFamily: data.fontFamily || defaultFontFamily,
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          borderRadius: 42,
          background: '#FFFFFF',
          overflow: 'hidden',
          border: '1px solid rgba(255, 255, 255, 0.70)',
          boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.80)',
        }}
      >
        <div
          style={{
            height: screenHeight,
            position: 'relative',
            overflow: 'hidden',
            background: 'linear-gradient(180deg, #020202 0%, #000000 55%, #090909 100%)',
          }}
        >
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background:
                'radial-gradient(circle at 50% 10%, rgba(255, 255, 255, 0.055), transparent 38%), linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0) 24%, rgba(0,0,0,0.55) 100%)',
            }}
          />
          <div
            style={{
              position: 'absolute',
              top: 26,
              right: 24,
              color: '#FFFFFF',
              opacity: 0.95,
              filter: 'drop-shadow(0 4px 10px rgba(0, 0, 0, 0.75))',
            }}
          >
            <CameraIcon size={34} />
          </div>

          {data.videoLabel ? (
            <div
              style={{
                position: 'absolute',
                left: 34,
                right: 92,
                top: '42%',
                transform: 'translateY(-50%)',
                color: data.accent,
                fontWeight: 950,
                fontSize: 44,
                lineHeight: 0.94,
                letterSpacing: 0,
                textShadow: '0 4px 16px rgba(0, 0, 0, 0.92)',
              }}
            >
              {data.videoLabel}
            </div>
          ) : null}

          <div
            style={{
              position: 'absolute',
              right: 20,
              bottom: railBottom,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 18,
            }}
          >
            <ReelAction icon={<HeartIcon size={36} />} label={data.likeCount} />
            <ReelAction icon={<CommentIcon size={36} />} label={data.commentCount} />
            <ReelAction icon={<SendIcon size={36} />} label={data.shareCount} />
            <MoreIcon size={34} color="#FFFFFF" />
            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: 12,
                border: '2.5px solid rgba(255, 255, 255, 0.9)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                background: 'rgba(255, 255, 255, 0.08)',
              }}
            >
              <MusicIcon size={24} />
            </div>
          </div>

          <div
            style={{
              position: 'absolute',
              left: 28,
              right: 88,
              bottom: 22,
              color: '#FFFFFF',
              textShadow: '0 3px 10px rgba(0, 0, 0, 0.9)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 11,
                marginBottom: 7,
              }}
            >
              <AvatarImage src={data.avatar} size={39} />
              <div
                style={{
                  fontWeight: 900,
                  fontSize: 20,
                  lineHeight: 1,
                }}
              >
                {data.username}
              </div>
              {data.verified ? <VerifiedBadge size={20} /> : null}
              <div
                style={{
                  border: '1.6px solid rgba(255, 255, 255, 0.65)',
                  borderRadius: 9,
                  padding: '5px 10px',
                  fontSize: 16,
                  lineHeight: 1,
                  fontWeight: 850,
                }}
              >
                Follow
              </div>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 7,
                fontSize: 18,
                fontWeight: 750,
                marginBottom: 9,
              }}
            >
              <MusicIcon size={18} />
              <span>{data.audio}</span>
            </div>
            <div
              style={{
                fontSize: 16,
                lineHeight: 1.15,
                fontWeight: 750,
                color: 'rgba(255, 255, 255, 0.92)',
                maxHeight: 38,
                overflow: 'hidden',
              }}
            >
              {previewCaption}
            </div>
          </div>
        </div>

        <div
          style={{
            height: navHeight,
            background: '#FFFFFF',
            color: '#000000',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-around',
            padding: '0 24px',
          }}
        >
          <BottomNavItem><HomeIcon size={32} /></BottomNavItem>
          <BottomNavItem><SearchIcon size={33} /></BottomNavItem>
          <BottomNavItem><PlusIcon size={32} /></BottomNavItem>
          <BottomNavItem active><ReelsIcon size={34} /></BottomNavItem>
          <BottomNavItem><ProfileIcon size={32} /></BottomNavItem>
        </div>
      </div>
    </div>
  );
};

export const SocialOverlayLayer = ({overlays}) => {
  const {fps} = useVideoConfig();

  return (
    <>
      {(overlays ?? []).map((overlay, index) => {
        if (!['instagram_float', 'instagram_reel_mock'].includes(overlay.type)) {
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
            {overlay.type === 'instagram_reel_mock' ? (
              <InstagramReelMockOverlay
                overlay={overlay}
                durationInFrames={endFrame - startFrame}
              />
            ) : (
              <FloatingInstagramOverlay
                overlay={overlay}
                durationInFrames={endFrame - startFrame}
              />
            )}
          </Sequence>
        );
      })}
    </>
  );
};
