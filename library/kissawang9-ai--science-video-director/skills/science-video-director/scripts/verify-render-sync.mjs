#!/usr/bin/env node

import {execFileSync} from 'node:child_process';
import {existsSync} from 'node:fs';

const [file, expectedFpsArg = '30', toleranceArg = '0.15'] = process.argv.slice(2);

if (!file || !existsSync(file)) {
  console.error('Usage: node verify-render-sync.mjs <video.mp4> [expected-fps=30] [duration-tolerance=0.15]');
  process.exit(2);
}

const expectedFps = Number(expectedFpsArg);
const durationTolerance = Number(toleranceArg);

if (!Number.isFinite(expectedFps) || expectedFps <= 0 || !Number.isFinite(durationTolerance) || durationTolerance < 0) {
  console.error('Expected fps and duration tolerance must be valid positive numbers.');
  process.exit(2);
}

const raw = execFileSync('ffprobe', [
  '-v', 'error',
  '-show_entries', 'format=duration:stream=index,codec_type,codec_name,avg_frame_rate,r_frame_rate,duration,nb_frames,width,height,sample_rate,channels',
  '-of', 'json',
  file,
], {encoding: 'utf8'});

const probe = JSON.parse(raw);
const video = probe.streams?.find((stream) => stream.codec_type === 'video');
const audio = probe.streams?.find((stream) => stream.codec_type === 'audio');

const parseRate = (value) => {
  const [numerator, denominator] = String(value || '0/1').split('/').map(Number);
  return denominator ? numerator / denominator : 0;
};

const fps = parseRate(video?.avg_frame_rate || video?.r_frame_rate);
const videoDuration = Number(video?.duration || probe.format?.duration || 0);
const audioDuration = Number(audio?.duration || probe.format?.duration || 0);
const frameCount = Number(video?.nb_frames || 0);
const expectedFrameCount = Math.round(videoDuration * fps);
const frameTolerance = Math.max(2, Math.ceil(fps * 0.05));
const errors = [];

if (!video) errors.push('missing video stream');
if (!audio) errors.push('missing audio stream');
if (video && Math.abs(fps - expectedFps) > 0.001) errors.push(`fps ${fps} does not match expected ${expectedFps}`);
if (video && frameCount > 0 && Math.abs(frameCount - expectedFrameCount) > frameTolerance) {
  errors.push(`frame count ${frameCount} is inconsistent with duration × fps (${expectedFrameCount})`);
}
if (video && audio && Math.abs(videoDuration - audioDuration) > durationTolerance) {
  errors.push(`audio/video duration delta ${Math.abs(videoDuration - audioDuration).toFixed(3)}s exceeds ${durationTolerance}s`);
}

const summary = {
  ok: errors.length === 0,
  file,
  video: video ? {
    codec: video.codec_name,
    width: video.width,
    height: video.height,
    fps,
    duration: videoDuration,
    frames: frameCount || null,
  } : null,
  audio: audio ? {
    codec: audio.codec_name,
    sampleRate: Number(audio.sample_rate || 0),
    channels: audio.channels,
    duration: audioDuration,
  } : null,
  expectedFps,
  durationTolerance,
  errors,
};

console.log(JSON.stringify(summary, null, 2));
process.exit(errors.length === 0 ? 0 : 1);
