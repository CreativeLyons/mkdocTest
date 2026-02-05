#!/usr/bin/env python3
"""
Parse the Google Docs HTML export to map images to tools.
Outputs a JSON file with tool -> images mapping.
"""

import re
import json
from pathlib import Path

HTML_FILE = "/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html"
OUTPUT_FILE = "/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/image-mapping.json"

# Tool name patterns (from tool-inventory.json)
TOOL_NAMES = [
    "LabelFromRead",
    "GradMagic", "NoiseAdvanced", "RadialAdvanced", "UV_Map", "WaterLens", "Silk",
    "Gradient Editor", "VoronoiGradient", "CellNoise", "LineTool", "PlotScanline",
    "SliceTool", "PerspectiveGuide", "DasGrain", "LumaGrain", "GrainAdvanced",
    "X_Tesla", "SpotFlare", "FlareSuperStar", "AutoFlare",
    "apLoop", "Looper", "FrameMedian", "TimeMachine", "FrameFiller",
    "BinaryAlpha", "ChannelCombiner", "ChannelControl", "ChannelCreator",
    "InjectMatteChannel", "StreamCart", "RenameChannels",
    "BlacksMatch", "ColorCopy", "Contrast", "GradeLayerPass", "HighlightSuppress",
    "ShadowMult", "WhiteSoftClip", "WhiteBalance", "apColorSampler", "apVignette",
    "GammaPlus", "MonochromePlus", "Suppress_RGBCMY", "BiasedSaturation", "HSL_Tool",
    "apGlow", "ExponGlow", "Glow_Exponential", "Optical Glow",
    "ExponBlurSimple", "Directional Blur", "IBlur", "WaveletBlur", "FractalBlur",
    "apEdgePush", "EdgeDetectAlias", "AntiAliasFilter", "ErodeSmooth", "Edge_RimLight",
    "EdgeDetectPRO", "Erode_Fine", "Edge_Expand", "Edge", "ColourSmear", "KillOutline",
    "EdgeFromAlpha", "VectorExtendEdge",
    "Glass", "HeatWave", "X_Distort", "X_Aton", "X_Denoise", "X_Sharpen", "X_Soften",
    "BeautifulSkin", "BlacksExpon", "Halation", "Highpass", "Diffusion", "LightWrapPro",
    "bm_Lightwrap", "iConvolve", "ConvolutionMatrix",
    "apChroma", "Chromatik", "CatsEyeDefocus", "DefocusSwirlyBokeh", "deHaze",
    "RankFilter", "DeflickerVelocity", "FillSampler", "MECfiller",
    "apDespill", "SpillCorrect", "DespillToColor", "AdditiveKeyerPro",
    "apeScreenClean", "apScreenGrow", "KeyChew", "LumaKeyer",
    "ContactSheetAuto", "KeymixBBox", "MergeAtmos", "MergeBlend", "MergeAll",
    "Vector Math Tools", "VectorTracker", "AutoCropTool", "BBoxToFormat", "ImagePlane3D",
    "Matrix4x4_Inverse", "Matrix4x4_Math", "MirrorBorder", "TransformCutOut", "iMorph",
    "RP_Reformat", "InverseMatrix33", "InverseMatrix44", "CardToTrack", "CProject", "TProject",
    "STiCKiT", "TransformMatrix", "CornerPin2D_Matrix", "IIDistort", "CameraShake",
    "MorphDissolve", "ITransform", "RotoCentroid", "STMapInverse", "Transform_Mix",
    "PlanarProjection", "Reconcile3DFast",
    "aPCard", "DummyCam", "mScatterGeo", "Origami", "RayDeepAO", "SceneDepthCalculator",
    "SSMesh", "Unify3DCoordinate", "UVEditor", "Distance3D", "DistanceBetween_CS",
    "Lightning3D", "GeoToPoints", "Noise3DTexture", "GodRaysProjector",
    "WaterSchmutz", "Sparky", "RainMaker", "ParticleLights", "ParticleKiller",
    "Deep2VP", "DeepFromDepth", "DeepToPosition", "DeepRecolorMatte", "DeepMerge_Advanced",
    "DeepCropSoft", "DeepKeyMix", "DeepHoldoutSmoother", "DeepCopyBBox", "DeepBoolean",
    "DeepFromPosition", "DeepSampleCount", "DeepSer",
    "UV_Mapper", "PNZ Suite", "Pos Toolkit", "Noise3D", "Noise4D", "Relight_Simple",
    "Reproject3D", "C44Kernal", "apDirLight", "apFresnel", "CameraNormals", "NormalsRotate",
    "EnvReflect_BB", "Relight_BB", "N_Reflection", "SimpleSSS", "aPmatte", "P_Project",
    "GlueP", "P_Ramp", "P_NoiseAdvanced",
    "WaveMachine", "Randomizer", "AnimationCurve", "CurveRemapper", "NoiseGen",
    "GUI_Switch", "NAN_INF_Killer", "apViewerBlocker", "Python_and_TCL", "RotoQC",
    "bm_MatteCheck", "ViewerRender", "NukeZ", "Pyclopedia",
    "Advanced Keying Template", "STMap Keyer Setup", "Gizmo Demo Scripts"
]

def main():
    # Read HTML
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find all image references
    image_pattern = r'<img[^>]*src="images/(image\d+\.(png|jpg|gif))"[^>]*>'
    all_images = re.findall(image_pattern, html)
    print(f"Found {len(all_images)} image references")
    
    # Build a mapping by finding tool names and their nearby images
    # We'll search for each tool name and extract surrounding context
    tool_images = {}
    
    for tool in TOOL_NAMES:
        # Escape special regex chars
        tool_escaped = re.escape(tool)
        # Find the tool name in the HTML
        pattern = rf'{tool_escaped}\s*(TL|AP|MJT|MHD|AG|SPIN|FR|XM|NKPD|BM|DR|EL|AK|FL|CF|RB|RK|FH|DB|LS|JP|MGA-EL|VARIOUS)?'
        matches = list(re.finditer(pattern, html, re.IGNORECASE))
        
        if matches:
            # Get position of first match
            start_pos = matches[0].start()
            # Find next tool (approximately 5000 chars ahead as a window)
            end_pos = min(start_pos + 10000, len(html))
            section = html[start_pos:end_pos]
            
            # Extract images in this section
            section_images = re.findall(r'images/(image\d+\.(png|jpg|gif))', section)
            if section_images:
                # Remove duplicates while preserving order
                seen = set()
                unique_images = []
                for img in section_images:
                    if img[0] not in seen:
                        seen.add(img[0])
                        unique_images.append(img[0])
                tool_images[tool] = unique_images[:5]  # Limit to 5 images per tool
    
    print(f"Mapped images for {len(tool_images)} tools")
    
    # Save mapping
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tool_images, f, indent=2)
    
    print(f"Saved to {OUTPUT_FILE}")
    
    # Print summary
    tools_with_images = sum(1 for t in tool_images if tool_images[t])
    total_images_mapped = sum(len(imgs) for imgs in tool_images.values())
    print(f"Tools with images: {tools_with_images}")
    print(f"Total images mapped: {total_images_mapped}")

if __name__ == "__main__":
    main()
