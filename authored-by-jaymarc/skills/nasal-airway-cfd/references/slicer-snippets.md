# Slicer-Python snippets

All of this runs inside Slicer via the `slicer` MCP `execute_python_code` tool.
Assign your return value to `__execResult`. numpy and scipy are available.
Adapt names/paths/parameters — these are building blocks, not a fixed script.

## Load a volume + sensible window

```python
import slicer
slicer.mrmlScene.Clear(0)                       # optional: fresh start
vol=slicer.util.loadVolume("/abs/path/scan.nrrd")
d=vol.GetDisplayNode(); d.SetAutoWindowLevel(False); d.SetWindow(2000); d.SetLevel(300)
slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
b=[0]*6; vol.GetRASBounds(b)                     # GetRASBounds takes the list arg
import numpy as np
arr=slicer.util.arrayFromVolume(vol)            # (Z,Y,X) view
__execResult={"dims":list(vol.GetImageData().GetDimensions()),
              "spacing":[round(s,3) for s in vol.GetSpacing()],
              "HU":[int(arr.min()),int(arr.max())],"RAS_bounds":[round(x,1) for x in b]}
```

## Jump to an anatomical level and screenshot

`FitSliceToAll()` resets the offset to volume center — call it FIRST, set offset
AFTER. Then capture `view_type="application"` (four-up); the dedicated "slice"
capture mode uses a different (relative) offset convention.

```python
import slicer, vtk
M=vtk.vtkMatrix4x4(); vol.GetIJKToRASMatrix(M)
ras=lambda i,j,k:[M.MultiplyPoint([i,j,k,1])[r] for r in range(3)]
cc=ras(mid_i, j_centroid, kz)                   # IJK target -> RAS
m=slicer.app.layoutManager()
for v in ["Red","Green","Yellow"]: m.sliceWidget(v).sliceLogic().FitSliceToAll()
m.sliceWidget("Red").sliceLogic().SetSliceOffset(cc[2])     # axial   = S
m.sliceWidget("Green").sliceLogic().SetSliceOffset(cc[1])   # coronal = A
m.sliceWidget("Yellow").sliceLogic().SetSliceOffset(cc[0])  # sagittal= L
```

Zoom an axial onto the nose for septum/coverage review:
```python
red=slicer.app.layoutManager().sliceWidget("Red").sliceLogic(); n=red.GetSliceNode()
fov=n.GetFieldOfView(); n.SetFieldOfView(95, 95*fov[1]/fov[0], fov[2]); red.SetSliceOffset(cc[2]); n.Modified()
```

## Threshold air → visible segmentation

A `vtkMRMLScalarVolumeNode` is NOT a labelmap — make a real label volume.

```python
import slicer, numpy as np
arr=slicer.util.arrayFromVolume(vol); air=(arr>-1024)&(arr<-350)
labv=slicer.modules.volumes.logic().CreateAndAddLabelVolume(slicer.mrmlScene,vol,"airlbl")
la=slicer.util.arrayFromVolume(labv); la[:]=air.astype(la.dtype); slicer.util.arrayFromVolumeModified(labv)
seg=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode","air_all"); seg.CreateDefaultDisplayNodes()
slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labv,seg)
slicer.mrmlScene.RemoveNode(labv)
seg.GetDisplayNode().SetOpacity2DFill(0.5)
```

## Bounding ROI (faces = inlet/outlet)

Anchor on the enclosed-air extent, then let the user drag faces. The anterior
face → nostril inlets; inferior face → nasopharyngeal outlet at the hard palate.

```python
import slicer
roi=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode","NasalROI")
roi.SetCenter(cx,cy,cz)                          # pass python floats
roi.SetSize(sx,sy,sz)
rd=roi.GetDisplayNode(); rd.SetOpacity(0.25); rd.SetHandlesInteractive(True)
```

## Extract the airway inside the ROI (region-grow)

**Critical:** do NOT region-grow on raw air ∩ ROI. The nasal cavity is open to
the outside through the nostrils, so the moment the ROI contains any external
air (which it will unless the box faces are perfectly placed in tissue — they
never are), the grow leaks: you get a ~150+ cm³ blob that's mostly the external
air slab in front of the face. Tested and confirmed on real data.

**Use *enclosed* air instead** — per axial slice, drop the air components that
touch the slice border (those are external); keep only air surrounded by bone.
Intersect that with the ROI. This removes the external slab automatically, and
the airway's anterior edge lands naturally at the bony piriform aperture — a
clean inlet. The nasal cavity + nasopharynx (+ sinuses) come through; external
air does not. Then take the largest component (or seed it).

```python
import slicer, numpy as np, vtk
from scipy import ndimage
arr=slicer.util.arrayFromVolume(vol); air=(arr>-1024)&(arr<-350); nz,nj,ni=arr.shape
enc=np.zeros_like(air)                                    # enclosed (internal) air only
for z in range(nz):
    s=air[z]
    if not s.any(): continue
    lab,n=ndimage.label(s)
    b=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]))); b.discard(0)
    enc[z]=(~np.isin(lab,list(b)))&s
# ROI -> IJK index box
c=[0,0,0]; roi.GetCenter(c); s=roi.GetSize()              # GetSize() takes NO args, returns a tuple
R=vtk.vtkMatrix4x4(); vol.GetRASToIJKMatrix(R)
toijk=lambda p: np.array(R.MultiplyPoint([p[0],p[1],p[2],1])[:3])
cor=np.array([toijk([c[0]+sx*s[0]/2, c[1]+sy*s[1]/2, c[2]+sz*s[2]/2])
              for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)])
lo=np.floor(cor.min(0)).astype(int); hi=np.ceil(cor.max(0)).astype(int)
i0,i1=max(0,lo[0]),min(ni,hi[0]); j0,j1=max(0,lo[1]),min(nj,hi[1]); k0,k1=max(0,lo[2]),min(nz,hi[2])
box=np.zeros_like(enc); box[k0:k1,j0:j1,i0:i1]=enc[k0:k1,j0:j1,i0:i1]   # arr is (Z=k,Y=j,X=i)
lab,n=ndimage.label(box)
sizes=ndimage.sum(np.ones_like(lab),lab,range(1,n+1))
airway=(lab==int(np.argmax(sizes))+1)                     # largest internal component
```

Sanity check the volume: nasal cavity + nasopharynx + sinuses is roughly
40–70 cm³; nasal + nasopharynx alone (sinuses excluded) ~20–35 cm³. A result of
100+ cm³ means external air still leaked — recheck the enclosed-air step.

Import `airway` into a segmentation (same labelmap pattern as above) and review
before excluding sinuses.

## Smooth + export STL

```python
import slicer
# import 'airway' mask -> segmentation node 'airway_seg' (CreateAndAddLabelVolume + ImportLabelmap)
# light smoothing so turbinates survive:
seg=slicer.util.getNode("airway_seg")
seg.GetSegmentation().SetConversionParameter("Smoothing factor","0.3")
seg.CreateClosedSurfaceRepresentation()
# export the surface to a model, then STL (keeps RAS orientation)
shn=slicer.mrmlScene.GetSubjectHierarchyNode()
folder=shn.CreateFolderItem(shn.GetSceneItemID(),"airway_export")
slicer.modules.segmentations.logic().ExportAllSegmentsToModels(seg,folder)
model=slicer.util.getNodesByClass("vtkMRMLModelNode")[-1]
slicer.util.saveNode(model,"/abs/path/output/nasal_airway_cfd.stl")
```

For finer control (windowed-sinc), operate on the model polydata with
`vtkWindowedSincPolyDataFilter` (PassBand ~0.1, ~20 iterations,
FeatureEdgeSmoothing off, BoundarySmoothing off to preserve the flat
inlet/outlet patches).

## QC

```python
import vtk
poly=model.GetPolyData()
fe=vtk.vtkFeatureEdges(); fe.SetInputData(poly)
fe.BoundaryEdgesOn(); fe.NonManifoldEdgesOn(); fe.FeatureEdgesOff(); fe.ManifoldEdgesOff(); fe.Update()
conn=vtk.vtkPolyDataConnectivityFilter(); conn.SetInputData(poly); conn.SetExtractionModeToAllRegions(); conn.Update()
mp=vtk.vtkMassProperties(); tri=vtk.vtkTriangleFilter(); tri.SetInputData(poly); tri.Update()
mp.SetInputConnection(tri.GetOutputPort()); mp.Update()
__execResult={"components":conn.GetNumberOfExtractedRegions(),
              "open_edges":fe.GetOutput().GetNumberOfCells(),     # should = inlet+outlet rims only
              "volume_cm3":round(mp.GetVolume()/1000,1),"area_mm2":round(mp.GetSurfaceArea(),1)}
```

Report inlet/outlet **areas** and **hydraulic diameter** (`Dh ≈ 2*sqrt(A/π)`) per
opening rim (split the boundary edges by connectivity, fill each loop, measure) —
the user needs these for CFD boundary conditions. Triangle quality:
`vtkMeshQuality` (aspect ratio, min angle) — flag slivers (AR>5, min-angle<10°).
