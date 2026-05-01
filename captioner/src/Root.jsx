import React from 'react';
import {Composition} from 'remotion';
import {CaptionedVideo} from './CaptionedVideo.jsx';
import {CoverImage} from './CoverImage.jsx';

const defaultProps = {
  videoFileName: 'source.mp4',
  width: 1080,
  height: 1920,
  fps: 30,
  duration: 1,
  pages: [],
  overlays: [],
  captionVariant: 'founder_clean',
  safeZone: {top: 0.12, bottom: 0.22, left: 0.08, right: 0.08},
  style: {
    fontFamily: 'Manrope',
    fontWeight: 800,
    fontSize: 88,
    textColor: '#FFFFFF',
    activeColor: '#FFA395',
    emphasisColor: '#FFA395',
    strokeColor: '#0A0A0A',
    backColor: '#0A0A0A',
    activeScale: 1.12,
    pageEnterFrames: 5,
    boxAlpha: 0.72,
    uppercase: false,
  },
};

export const Root = () => {
  return (
    <>
      <Composition
        id="CaptionedVideo"
        component={CaptionedVideo}
        width={1080}
        height={1920}
        fps={30}
        durationInFrames={30}
        defaultProps={defaultProps}
        calculateMetadata={({props}) => {
          const fps = props.fps ?? 30;
          return {
            width: props.width ?? 1080,
            height: props.height ?? 1920,
            fps,
            durationInFrames: Math.max(1, Math.ceil((props.duration ?? 1) * fps)),
          };
        }}
      />
      <Composition
        id="CoverImage"
        component={CoverImage}
        width={2160}
        height={3840}
        fps={30}
        durationInFrames={1}
        defaultProps={{
          imageFileName: 'cover.png',
          variant: 'outplayed',
        }}
      />
    </>
  );
};
