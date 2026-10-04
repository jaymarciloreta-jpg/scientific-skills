# Premiere handoff

Use the `.xml` produced by `build_timeline.py`: Final Cut Pro 7 XML (`xmeml`,
version 5), including linked video and mono/stereo source audio. Import it into
Premiere and verify relinking, dimensions, frame rate, synchronization, and cut
boundaries. The exporter has synthetic structural tests but has not yet passed
an actual Premiere application import test.

The old skill incorrectly claimed `.fcpxml` was directly importable. Adobe
explicitly documents conversion from Final Cut Pro X `.fcpxml` to Premiere's
supported XML interchange:
[Adobe import documentation](https://helpx.adobe.com/premiere/desktop/organize-media/import-files/migrate-from-final-cut-pro-x.html)
(accessed 2026-10-04).

The `.edl` is a video-only fallback for up to 999 events. It uses non-drop-frame
timecode and unique clip IDs; manual source relinking may be necessary. Do not
promise that every Premiere version will automatically relink an EDL.

## Editor checklist

- Match every imported source to the manifest; no missing or duplicated chunks.
- Check sequence frame rate/dimensions against the source.
- Check audio at the start, near the middle, and after edits.
- Compare cut boundaries with the reviewed source intervals.
- Confirm protected moments are present.
- Preserve the original manifest, session, decision JSON, and audit with the edit.

## README_edit template

- Recording and revision:
- Ordering basis and confirmation:
- Source duration / retained duration:
- Review session ID and decisions filename:
- Protected intervals:
- Frame rate, dimensions, audio:
- Premiere version and import verification outcome:
- Remaining editorial changes:
