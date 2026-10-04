# Cohort survey & scan screening

## Ranking volumes (runs in host shell or Slicer Python)

NRRD headers are ASCII — parse without loading the pixel data. For each `.nrrd`,
read `sizes` and `space directions`, skip derived/scout/thick series, and rank
by slice thickness then in-plane spacing.

```python
import glob, os, re
def hdr(fn):
    d={}
    with open(fn,'rb') as f:
        for _ in range(80):
            line=f.readline()
            if line in (b'\n', b'\r\n', b''): break
            try: line=line.decode('ascii').strip()
            except: continue
            if ':' in line and not line.startswith('#'):
                k,_,v=line.partition(':'); d[k.strip().lower()]=v.strip().lstrip('=').strip()
    return d
def sp(sd):  # per-axis spacing = norm of each direction vector
    return [round(sum(float(x)**2 for x in v.split(','))**0.5,3)
            for v in re.findall(r'\(([^)]+)\)', sd)]

best={}
for fn in glob.glob('<cohort>/*/*/*.nrrd'):
    b=os.path.basename(fn)
    if 'DERIVED' in b or 'MIP' in b: continue          # skip reformats
    h=hdr(fn); sz=[int(x) for x in h.get('sizes','').split()] if h.get('sizes') else []
    if len(sz)<3 or sz[2]<40: continue                  # skip scouts
    s=sp(h.get('space directions',''))
    if len(s)<3: continue
    pat=fn.split('/')[0]
    score=(s[2], max(s[0],s[1]))                        # thin slice, then fine in-plane
    if pat not in best or score<best[pat][0]:
        best[pat]=(score,fn,sz,s)
```

A typical primary axial CT is `512×512×N` with in-plane ~0.3–0.5 mm. The full HU
range (~-1024..+3000) confirms it's a real CT (air to bone). Contrast-enhanced
(CTA) scans are fine — air is air regardless of contrast.

## Selection criteria

The dataset is likely from an ENT/sinus practice, so deviated septa, masses, and
cropped FOVs are common. Highest resolution ≠ usable. Require:

1. **Straight septum** — midline septal bone, both nasal passages patent and
   roughly symmetric. Severe deviation distorts the flow domain.
2. **No mass / tumor** — maxillary/ethmoid/sphenoid sinuses aerated (black, not
   opacified); skull base and nasopharynx unremarkable.
3. **Nose fully in FOV** — anterior nasal bones, columella, and nostril tips
   present, not clipped by the scan's anterior boundary.

You can observe these from imaging, but the **user is the clinical authority** —
present the axial and get their sign-off before committing.

## Landing on the nasal level — the maxillary-sinus detector

The mid-nasal axial level is uniquely fingerprinted by the **paired maxillary
sinuses**: two large enclosed-air regions flanking the nasal cavity. Maximize
the *smaller* of the best left and best right enclosed-air component — this
rejects the frontal sinus (single, midline, superior) and mastoids (lateral but
posterior, and not a symmetric anterior pair at the right level).

```python
import numpy as np, vtk
from scipy import ndimage
arr=slicer.util.arrayFromVolume(v)      # (Z, Y, X)
nz,nj,ni=arr.shape
air=(arr>-1024)&(arr<-350); mid_i=ni//2
best=(-1, nz//2)
for z in range(nz):
    s=air[z]
    if s.sum()<500: continue
    lab,n=ndimage.label(s)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]))); border.discard(0)
    enc=(~np.isin(lab,list(border)))&s            # enclosed (internal) air only
    el,en=ndimage.label(enc)
    if en==0: continue
    sizes=ndimage.sum(np.ones_like(el),el,range(1,en+1))
    coms=ndimage.center_of_mass(np.ones_like(el),el,range(1,en+1))
    left =[sizes[k] for k in range(en) if coms[k][1] < mid_i-20]
    right=[sizes[k] for k in range(en) if coms[k][1] > mid_i+20]
    if left and right:
        score=min(max(left),max(right))           # strong on BOTH sides
        if score>best[0]: best=(score,z)
kz=best[1]                                          # nasal axial IJK slice
```

Convert `kz` to a RAS S offset with the IJK→RAS matrix, then display (see
slicer-snippets `## Jump to a level and screenshot`). Zoom the axial to ~95 mm
FOV around the nose to read the septum and nostril coverage clearly.
