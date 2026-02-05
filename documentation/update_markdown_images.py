#!/usr/bin/env python3
"""
Update markdown files with images from image-mapping.json
"""

import json
import os
import re
from pathlib import Path

DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")
IMAGE_MAPPING = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/image-mapping.json")
IMAGES_DIR = DOCS_DIR / "img" / "tools"

# Mapping from markdown filename to tool name in image-mapping.json
# Some names don't match exactly, so we need this mapping
FILENAME_TO_TOOL = {
    "labelfromread": "LabelFromRead",
    "grad-magic": "GradMagic",
    "noise-advanced": "NoiseAdvanced",
    "radial-advanced": "RadialAdvanced",
    "uv-map": "UV_Map",
    "water-lens": "WaterLens",
    "silk": "Silk",
    "gradient-editor": "Gradient Editor",
    "voronoi-gradient": "VoronoiGradient",
    "cell-noise": "CellNoise",
    "line-tool": "LineTool",
    "plot-scanline": "PlotScanline",
    "slice-tool": "SliceTool",
    "perspective-guide": "PerspectiveGuide",
    "das-grain": "DasGrain",
    "luma-grain": "LumaGrain",
    "grain-advanced": "GrainAdvanced",
    "x-tesla": "X_Tesla",
    "spot-flare": "SpotFlare",
    "flare-super-star": "FlareSuperStar",
    "auto-flare": "AutoFlare",
    "ap-loop": "apLoop",
    "looper": "Looper",
    "frame-median": "FrameMedian",
    "time-machine": "TimeMachine",
    "frame-filler": "FrameFiller",
    "binary-alpha": "BinaryAlpha",
    "channel-combiner": "ChannelCombiner",
    "channel-control": "ChannelControl",
    "channel-creator": "ChannelCreator",
    "inject-matte-channel": "InjectMatteChannel",
    "stream-cart": "StreamCart",
    "rename-channels": "RenameChannels",
    "blacks-match": "BlacksMatch",
    "color-copy": "ColorCopy",
    "contrast": "Contrast",
    "grade-layer-pass": "GradeLayerPass",
    "highlight-suppress": "HighlightSuppress",
    "shadow-mult": "ShadowMult",
    "white-soft-clip": "WhiteSoftClip",
    "white-balance": "WhiteBalance",
    "ap-color-sampler": "apColorSampler",
    "ap-vignette": "apVignette",
    "gamma-plus": "GammaPlus",
    "monochrome-plus": "MonochromePlus",
    "suppress-rgbcmy": "Suppress_RGBCMY",
    "biased-saturation": "BiasedSaturation",
    "hsl-tool": "HSL_Tool",
    "ap-glow": "apGlow",
    "expon-glow": "ExponGlow",
    "glow-exponential": "Glow_Exponential",
    "optical-glow": "Optical Glow",
    "expon-blur-simple": "ExponBlurSimple",
    "directional-blur": "Directional Blur",
    "iblur": "IBlur",
    "wavelet-blur": "WaveletBlur",
    "fractal-blur": "FractalBlur",
    "ap-edge-push": "apEdgePush",
    "edge-detect-alias": "EdgeDetectAlias",
    "anti-alias-filter": "AntiAliasFilter",
    "erode-smooth": "ErodeSmooth",
    "edge-rim-light": "Edge_RimLight",
    "edge-detect-pro": "EdgeDetectPRO",
    "erode-fine": "Erode_Fine",
    "edge-expand": "Edge_Expand",
    "edge": "Edge",
    "colour-smear": "ColourSmear",
    "kill-outline": "KillOutline",
    "edge-from-alpha": "EdgeFromAlpha",
    "vector-extend-edge": "VectorExtendEdge",
    "glass": "Glass",
    "heat-wave": "HeatWave",
    "x-distort": "X_Distort",
    "x-aton": "X_Aton",
    "x-denoise": "X_Denoise",
    "x-sharpen": "X_Sharpen",
    "x-soften": "X_Soften",
    "beautiful-skin": "BeautifulSkin",
    "blacks-expon": "BlacksExpon",
    "halation": "Halation",
    "highpass": "Highpass",
    "diffusion": "Diffusion",
    "lightwrap-pro": "LightWrapPro",
    "bm-lightwrap": "bm_Lightwrap",
    "iconvolve": "iConvolve",
    "convolution-matrix": "ConvolutionMatrix",
    "apchroma": "apChroma Tools",
    "chromatik": "Chromatik",
    "cats-eye-defocus": "CatsEyeDefocus",
    "defocus-swirly-bokeh": "DefocusSwirlyBokeh",
    "dehaze": "deHaze",
    "deflicker-velocity": "DeflickerVelocity",
    "fill-sampler": "FillSampler",
    "mec-filler": "MECfiller",
    "rank-filter": "RankFilter",
    "ap-despill": "apDespill",
    "spill-correct": "SpillCorrect",
    "despill-to-color": "DespillToColor",
    "additive-keyer-pro": "AdditiveKeyerPro",
    "ape-screen-clean": "apeScreenClean",
    "ap-screen-grow": "apScreenGrow",
    "key-chew": "KeyChew",
    "luma-keyer": "LumaKeyer",
    "contact-sheet-auto": "ContactSheetAuto",
    "keymix-bbox": "KeymixBBox",
    "merge-atmos": "MergeAtmos",
    "merge-blend": "MergeBlend",
    "merge-all": "MergeAll",
    "vector-math-tools": "Vector Math Tools",
    "vector-tracker": "VectorTracker",
    "auto-crop-tool": "AutoCropTool",
    "bbox-to-format": "BBoxToFormat",
    "matrix4x4-inverse": "Matrix4x4_Inverse",
    "matrix4x4-math": "Matrix4x4_Math",
    "mirror-border": "MirrorBorder",
    "transform-cut-out": "TransformCutOut",
    "imorph": "iMorph",
    "rp-reformat": "RP_Reformat",
    "inverse-matrix33": "InverseMatrix33",
    "inverse-matrix44": "InverseMatrix44",
    "card-to-track": "CardToTrack",
    "cproject": "CProject",
    "tproject": "TProject",
    "stickit": "STiCKiT",
    "transform-matrix": "TransformMatrix",
    "cornerpin2d-matrix": "CornerPin2D_Matrix",
    "iidistort": "IIDistort",
    "camera-shake": "CameraShake",
    "morph-dissolve": "MorphDissolve",
    "itransform": "ITransform",
    "roto-centroid": "RotoCentroid",
    "stmap-inverse": "STMapInverse",
    "transform-mix": "Transform_Mix",
    "planar-projection": "PlanarProjection",
    "reconcile3d-fast": "Reconcile3DFast",
    "ap-card": "aPCard",
    "dummy-cam": "DummyCam",
    "m-scatter-geo": "mScatterGeo",
    "origami": "Origami",
    "ray-deep-ao": "RayDeepAO",
    "scene-depth-calculator": "SceneDepthCalculator",
    "ss-mesh": "SSMesh",
    "unify-3d-coordinate": "Unify3DCoordinate",
    "uv-editor": "UVEditor",
    "distance-3d": "Distance3D",
    "distance-between-cs": "DistanceBetween_CS",
    "lightning-3d": "Lightning3D",
    "geo-to-points": "GeoToPoints",
    "noise-3d-texture": "Noise3DTexture",
    "god-rays-projector": "GodRaysProjector",
    "waterschmutz": "WaterSchmutz",
    "sparky": "Sparky",
    "rainmaker": "RainMaker",
    "particlelights": "ParticleLights",
    "particlekiller": "ParticleKiller",
    "deep2vp": "Deep2VP Suite",
    "deepfromdepth": "DeepFromDepth",
    "deeptoposition": "DeepToPosition",
    "deeprecolormatte": "DeepRecolorMatte",
    "deepmerge-advanced": "DeepMerge_Advanced",
    "deepcropsoft": "DeepCropSoft",
    "deepkeymix": "DeepKeyMix",
    "deepholdoutsmoother": "DeepHoldoutSmoother",
    "deepcopybbox": "DeepCopyBBox",
    "deepboolean": "DeepBoolean",
    "deepfromposition": "DeepFromPosition",
    "deepsamplecount": "DeepSampleCount",
    "deepser": "DeepSer",
    "uv-mapper": "UV_Mapper",
    "pnz-suite": "PNZ Suite",
    "pos-toolkit": "Pos Toolkit",
    "noise3d": "Noise3D",
    "noise4d": "Noise4D",
    "relight-simple": "Relight_Simple",
    "reproject3d": "Reproject3D",
    "c44kernal": "C44Kernal",
    "apdirlight": "apDirLight",
    "apfresnel": "apFresnel",
    "cameranormals": "CameraNormals",
    "normalsrotate": "NormalsRotate",
    "envreflect-bb": "EnvReflect_BB",
    "relight-bb": "Relight_BB",
    "n-reflection": "N_Reflection",
    "simplesss": "SimpleSSS",
    "apmatte": "aPmatte",
    "p-project": "P_Project",
    "gluep": "GlueP",
    "p-ramp": "P_Ramp",
    "p-noiseadvanced": "P_NoiseAdvanced",
    "wavemachine": "WaveMachine",
    "randomizer": "Randomizer",
    "animationcurve": "AnimationCurve",
    "curveremapper": "CurveRemapper",
    "noisegen": "NoiseGen",
    "gui-switch": "GUI_Switch",
    "nan-inf-killer": "NAN_INF_Killer",
    "apviewerblocker": "apViewerBlocker",
    "python-and-tcl": "Python_and_TCL",
    "rotoqc": "RotoQC",
    "bm-mattecheck": "bm_MatteCheck",
    "viewerrender": "ViewerRender",
    "nukez": "NukeZ",
    "pyclopedia": "Pyclopedia",
    "advanced-keying-template": "Advanced Keying Template",
    "advanced-keying-template-stamps": "Advanced Keying Template Stamps",
    "stmap-keyer-setup": "STMap Keyer Setup",
}

def get_tool_name(filename):
    """Get tool name from filename"""
    base = filename.replace('.md', '')
    if base in FILENAME_TO_TOOL:
        return FILENAME_TO_TOOL[base]
    return base

def update_markdown(filepath, images):
    """Update a markdown file with images"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if images already added
    if '## Images' in content and '![' in content.split('## Images')[-1]:
        return False  # Already has images
    
    # Create image markdown
    image_md = "\n\n## Images\n\n"
    for img in images[:5]:  # Limit to 5 images
        # Use relative path from the markdown file location
        image_md += f"![{img}](../img/tools/{img})\n\n"
    
    # Find where to add images (before any existing ## Images section or at end)
    if '## Images' in content:
        # Replace empty Images section
        content = re.sub(r'## Images\s*\n\s*(\[.*?\])?', image_md.strip() + '\n', content)
    else:
        # Add at end
        content = content.rstrip() + image_md
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return True

def main():
    # Load image mapping
    with open(IMAGE_MAPPING) as f:
        mapping = json.load(f)
    
    updated = 0
    not_found = 0
    
    # Walk through all markdown files
    for root, dirs, files in os.walk(DOCS_DIR):
        # Skip index files and top-level pages
        for fname in files:
            if not fname.endswith('.md'):
                continue
            if fname == 'index.md':
                continue
            if fname in ['about.md', 'installation.md', 'menus.md', 'techSpecs.md']:
                continue
            
            filepath = Path(root) / fname
            tool_name = get_tool_name(fname)
            
            if tool_name in mapping:
                images = mapping[tool_name]['images']
                if images:
                    if update_markdown(filepath, images):
                        updated += 1
                        print(f"Updated: {filepath.relative_to(DOCS_DIR)} with {len(images)} images")
            else:
                not_found += 1
                # Try fuzzy matching
                for key in mapping:
                    if key.lower().replace('_', '').replace(' ', '') == tool_name.lower().replace('-', '').replace('_', ''):
                        images = mapping[key]['images']
                        if images:
                            if update_markdown(filepath, images):
                                updated += 1
                                print(f"Updated (fuzzy): {filepath.relative_to(DOCS_DIR)} with {len(images)} images")
                                not_found -= 1
                        break
    
    print(f"\nTotal updated: {updated}")
    print(f"Not found in mapping: {not_found}")

if __name__ == "__main__":
    main()
