import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {defaultFontFamily} from './fonts.js';

const captionShadow = [
  '0 4px 4px rgba(0, 0, 0, 0.92)',
  '0 10px 20px rgba(0, 0, 0, 0.74)',
  '0 0 32px rgba(0, 0, 0, 0.62)',
  '0 0 60px rgba(0, 0, 0, 0.42)',
].join(', ');

const baseCaptionStyle = {
  fontFamily: defaultFontFamily,
  fontWeight: 800,
  letterSpacing: 0,
  color: '#FFFFFF',
  textShadow: captionShadow,
};

const CoverCaption = ({words}) => {
  return (
    <div
      style={{
        position: 'absolute',
        left: '8%',
        right: '8%',
        bottom: '22%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'baseline',
        columnGap: '0.18em',
        fontSize: 192,
        lineHeight: 1.02,
        ...baseCaptionStyle,
      }}
    >
      {words.map((word, index) => (
        <span key={`${word.text}-${index}`} style={{color: word.color ?? '#FFFFFF'}}>
          {word.text}
        </span>
      ))}
    </div>
  );
};

const StackedTitle = () => {
  return (
    <div
      style={{
        position: 'absolute',
        left: '7%',
        right: '7%',
        bottom: '16%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        ...baseCaptionStyle,
      }}
    >
      <div style={{fontSize: 270, lineHeight: 0.9}}>
        <span>Day </span>
        <span style={{color: '#FF5A4F'}}>one</span>
      </div>
      <div style={{fontSize: 150, lineHeight: 0.98, marginTop: 26}}>
        <span>training an </span>
        <span style={{color: '#FF5A4F'}}>AI</span>
      </div>
      <div style={{fontSize: 150, lineHeight: 0.98}}>video editor</div>
    </div>
  );
};

export const CoverImage = ({imageFileName, variant}) => {
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Img
        src={staticFile(imageFileName)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
      {variant === 'day-one' ? (
        <StackedTitle />
      ) : (
        <CoverCaption
          words={[
            {text: 'I'},
            {text: 'got'},
            {text: 'outplayed', color: '#FF5A4F'},
          ]}
        />
      )}
    </AbsoluteFill>
  );
};
