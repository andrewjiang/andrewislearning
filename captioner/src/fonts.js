import {continueRender, delayRender} from 'remotion';
import {loadFont as loadManrope} from '@remotion/google-fonts/Manrope';
import {loadFont as loadBebasNeue} from '@remotion/google-fonts/BebasNeue';
import {loadFont as loadKalam} from '@remotion/google-fonts/Kalam';
import {loadFont as loadAnton} from '@remotion/google-fonts/Anton';
import {loadFont as loadArchivoBlack} from '@remotion/google-fonts/ArchivoBlack';
import {loadFont as loadBarlowCondensed} from '@remotion/google-fonts/BarlowCondensed';
import {loadFont as loadInterTight} from '@remotion/google-fonts/InterTight';
import {loadFont as loadLeagueGothic} from '@remotion/google-fonts/LeagueGothic';
import {loadFont as loadMontserrat} from '@remotion/google-fonts/Montserrat';
import {loadFont as loadOswald} from '@remotion/google-fonts/Oswald';
import {loadFont as loadPermanentMarker} from '@remotion/google-fonts/PermanentMarker';
import {loadFont as loadPoppins} from '@remotion/google-fonts/Poppins';
import {loadFont as loadTeko} from '@remotion/google-fonts/Teko';
import {loadFont as loadTikTokSans} from '@remotion/google-fonts/TikTokSans';

const manrope = loadManrope('normal', {
  weights: ['400', '700', '800'],
  subsets: ['latin'],
});
const bebasNeue = loadBebasNeue('normal', {
  weights: ['400'],
  subsets: ['latin'],
});
const kalam = loadKalam('normal', {
  weights: ['700'],
  subsets: ['latin'],
});
const anton = loadAnton('normal', {
  weights: ['400'],
  subsets: ['latin'],
});
const archivoBlack = loadArchivoBlack('normal', {
  weights: ['400'],
  subsets: ['latin'],
});
const barlowCondensed = loadBarlowCondensed('normal', {
  weights: ['900'],
  subsets: ['latin'],
});
const interTight = loadInterTight('normal', {
  weights: ['900'],
  subsets: ['latin'],
});
const leagueGothic = loadLeagueGothic('normal', {
  weights: ['400'],
  subsets: ['latin'],
});
const montserrat = loadMontserrat('normal', {
  weights: ['900'],
  subsets: ['latin'],
});
const oswald = loadOswald('normal', {
  weights: ['700'],
  subsets: ['latin'],
});
const permanentMarker = loadPermanentMarker('normal', {
  weights: ['400'],
  subsets: ['latin'],
});
const poppins = loadPoppins('normal', {
  weights: ['900'],
  subsets: ['latin'],
});
const teko = loadTeko('normal', {
  weights: ['700'],
  subsets: ['latin'],
});
const tiktokSans = loadTikTokSans('normal', {
  weights: ['900'],
  subsets: ['latin'],
});

const captionFonts = [
  manrope,
  bebasNeue,
  kalam,
  anton,
  archivoBlack,
  barlowCondensed,
  interTight,
  leagueGothic,
  montserrat,
  oswald,
  permanentMarker,
  poppins,
  teko,
  tiktokSans,
];

const handle = delayRender('Loading caption fonts');
Promise.allSettled(captionFonts.map((font) => font.waitUntilDone()))
  .then((results) => {
    const failedFonts = results.filter((result) => result.status === 'rejected');
    if (failedFonts.length > 0) {
      console.warn(`Failed to load ${failedFonts.length} caption font family/families.`);
    }
    continueRender(handle);
  })
  .catch(() => continueRender(handle));

export const defaultFontFamily = manrope.fontFamily;
export const displayFontFamily = bebasNeue.fontFamily;
export const handwrittenFontFamily = kalam.fontFamily;
export const captionFontFamilies = {
  manrope: manrope.fontFamily,
  bebasNeue: bebasNeue.fontFamily,
  kalam: kalam.fontFamily,
  anton: anton.fontFamily,
  archivoBlack: archivoBlack.fontFamily,
  barlowCondensed: barlowCondensed.fontFamily,
  interTight: interTight.fontFamily,
  leagueGothic: leagueGothic.fontFamily,
  montserrat: montserrat.fontFamily,
  oswald: oswald.fontFamily,
  permanentMarker: permanentMarker.fontFamily,
  poppins: poppins.fontFamily,
  teko: teko.fontFamily,
  tiktokSans: tiktokSans.fontFamily,
};

const normalizeFontKey = (value) => String(value || '')
  .trim()
  .toLowerCase()
  .replace(/[^a-z0-9]/g, '');

const fontAliases = new Map([
  ['manrope', captionFontFamilies.manrope],
  ['bebasneue', captionFontFamilies.bebasNeue],
  ['display', captionFontFamilies.bebasNeue],
  ['kalam', captionFontFamilies.kalam],
  ['handwritten', captionFontFamilies.kalam],
  ['anton', captionFontFamilies.anton],
  ['archivoblack', captionFontFamilies.archivoBlack],
  ['barlowcondensed', captionFontFamilies.barlowCondensed],
  ['intertight', captionFontFamilies.interTight],
  ['leaguegothic', captionFontFamilies.leagueGothic],
  ['montserrat', captionFontFamilies.montserrat],
  ['oswald', captionFontFamilies.oswald],
  ['permanentmarker', captionFontFamilies.permanentMarker],
  ['marker', captionFontFamilies.permanentMarker],
  ['poppins', captionFontFamilies.poppins],
  ['teko', captionFontFamilies.teko],
  ['tiktoksans', captionFontFamilies.tiktokSans],
  ['tiktok', captionFontFamilies.tiktokSans],
]);

export const resolveCaptionFontFamily = (fontFamily, fallback = defaultFontFamily) => {
  if (!fontFamily) {
    return fallback;
  }
  return fontAliases.get(normalizeFontKey(fontFamily)) || fontFamily || fallback;
};
