#!/usr/bin/env python3
"""
Full audit: Cross-reference every tool section in the Google Doc HTML export
against every markdown page to find image mismatches.

For each tool, compare:
- Images in Google Doc (source of truth)
- Images in markdown wiki

Report:
- Extra images in markdown (not in Google Doc for that tool)
- Missing images from markdown (in Google Doc but not in markdown)
- Images assigned to wrong tool
"""

import re
from pathlib import Path
from collections import defaultdict, OrderedDict

GDOC_HTML = Path("/Users/tonylyons/Downloads/NukeSurvivalToolkit_Documentation_v2.1.0/NukeSurvivalToolkit_Documentation_v2.1.0.html")
DOCS_DIR = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/documentation/docs")
RENAME_MAP = Path("/Users/tonylyons/Dropbox/Public/GitHub/mkdocTest/rename_map.txt")

def load_rename_map():
    """old_name -> new_name"""
    rmap = {}
    for line in RENAME_MAP.read_text().strip().split('\n'):
        if ' -> ' in line:
            old, new = line.split(' -> ', 1)
            rmap[old.strip()] = new.strip()
    return rmap

def load_reverse_map():
    """new_name -> old_name"""
    rmap = load_rename_map()
    return {v: k for k, v in rmap.items()}

def parse_gdoc():
    """Parse Google Doc HTML -> OrderedDict of section_name -> [original_image_names]"""
    html = GDOC_HTML.read_text(encoding="utf-8", errors="replace")

    elements = []
    for m in re.finditer(r'<h([1-6])[^>]*>(.*?)</h\1>', html, re.DOTALL):
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        text = re.sub(r'&nbsp;', ' ', text).strip()
        if text:
            elements.append(('heading', m.start(), text))

    for m in re.finditer(r'<img[^>]*src="images/(image\d+\.\w+)"[^>]*/?>',  html):
        elements.append(('image', m.start(), m.group(1)))

    elements.sort(key=lambda x: x[1])

    sections = OrderedDict()
    current = "Preamble"
    sections[current] = []

    for elem_type, pos, content in elements:
        if elem_type == 'heading':
            current = content
            if current not in sections:
                sections[current] = []
        elif elem_type == 'image':
            sections[current].append(content)

    return sections

def parse_markdown_images():
    """Parse all markdown files -> dict of md_path -> [new_image_names]"""
    md_images = {}

    for md_file in DOCS_DIR.rglob("*.md"):
        rel = str(md_file.relative_to(DOCS_DIR))
        content = md_file.read_text(encoding="utf-8", errors="replace")

        images = []
        for m in re.finditer(r'img/tools/(?:[a-zA-Z0-9_/-]+/)?([a-zA-Z0-9_.-]+\.[a-z]+)', content):
            img_name = m.group(1)
            # Skip video thumbnails
            if 'thumb' in img_name:
                continue
            # Skip non-tool images (splash page, menu screenshots from img/ root)
            images.append(img_name)

        if images:
            md_images[rel] = images

    return md_images

# Mapping of Google Doc headings -> markdown file paths
GDOC_TO_MD = {
    "Preamble": "index.md",
    "Installation": "installation.md",
    "Menus": "menus.md",
    "LabelFromRead TL": "image/labelfromread.md",
    "Expression Nodes AG Menu": "draw/expression-ag/index.md",
    "GradMagic TL": "draw/grad-magic.md",
    "NoiseAdvanced TL": "draw/noise-advanced.md",
    "RadialAdvanced TL": "draw/radial-advanced.md",
    "UV_Map AG": "draw/expression-ag/uv-map.md",
    "WaterLens MJT": "draw/water-lens.md",
    "Silk MHD": "draw/hagbarth/silk.md",
    "Gradient Editor MHD": "draw/hagbarth/gradient-editor.md",
    "VoronoiGradient NKPD": "draw/voronoi-gradient.md",
    "CellNoise NKPD": "draw/cell-noise.md",
    "LineTool NKPD": "draw/line-tool.md",
    "PlotScanline NKPD": "draw/plot-scanline.md",
    "SliceTool NKPD": "draw/slice-tool.md",
    "PerspectiveGuide NKPD": "draw/perspective-guide.md",
    "DasGrain NKPD": "draw/das-grain.md",
    "LumaGrain NKPD": "draw/luma-grain.md",
    "GrainAdvanced NKPD": "draw/grain-advanced.md",
    "X_Tesla XM": "draw/x-tesla.md",
    "FlareSuperStar NKPD": "draw/flare-super-star.md",
    "AutoFlare NKPD": "draw/auto-flare.md",
    "SpotFlare MHD": "draw/hagbarth/spot-flare.md",
    "apLoop AP": "time/ap-loop.md",
    "Looper NKPD": "time/looper.md",
    "FrameMedian MHD": "time/frame-median.md",
    "TimeMachine NKPD": "time/time-machine.md",
    "FrameFiller MJT": "time/frame-filler.md",
    "BinaryAlpha TL": "channel/binary-alpha.md",
    "ChannelCombiner NKPD": "channel/channel-combiner.md",
    "ChannelControl NKPD": "channel/channel-control.md",
    "ChannelCreator NKPD": "channel/channel-creator.md",
    "InjectMatteChannel NKPD": "channel/inject-matte-channel.md",
    "StreamCart NKPD": "channel/stream-cart.md",
    "RenameChannels NKPD": "channel/rename-channels.md",
    "BlacksMatch TL": "color/blacks-match.md",
    "ColorCopy NKPD": "color/color-copy.md",
    "Contrast NKPD": "color/contrast.md",
    "GradeLayerPass NKPD": "color/grade-layer-pass.md",
    "HighlightSuppress NKPD": "color/highlight-suppress.md",
    "ShadowMult NKPD": "color/shadow-mult.md",
    "WhiteSoftClip NKPD": "color/white-soft-clip.md",
    "WhiteBalance NKPD": "color/white-balance.md",
    "apColorSampler AP": "color/ap-color-sampler.md",
    "apVignette AP": "color/ap-vignette.md",
    "GammaPlus TL": "color/gamma-plus.md",
    "MonochromePlus TL": "color/monochrome-plus.md",
    "Suppress_RGBCMY TL": "color/suppress-rgbcmy.md",
    "BiasedSaturation NKPD": "color/biased-saturation.md",
    "HSL_Tool NKPD": "color/hsl-tool.md",
    "apGlow AP": "filter/glows/ap-glow.md",
    "ExponGlow TL": "filter/glows/expon-glow.md",
    "Glow_Exponential SPIN": "filter/glows/glow-exponential.md",
    "Optical Glow BM": "filter/glows/optical-glow.md",
    "ExponBlurSimple TL": "filter/blur/expon-blur-simple.md",
    "Directional Blur TL": "filter/blur/directional-blur.md",
    "IBlur NKPD": "filter/blur/iblur.md",
    "WaveletBlur MHD": "filter/blur/wavelet-blur.md",
    "FractalBlur NKPD": "filter/blur/fractal-blur.md",
    "apEdgePush AP": "filter/edges/ap-edge-push.md",
    "EdgeDetectAlias NKPD": "filter/edges/edge-detect-alias.md",
    "AntiAliasFilter AG": "filter/edges/anti-alias-filter.md",
    "ErodeSmooth TL": "filter/edges/erode-smooth.md",
    "Edge_RimLight AG": "filter/edges/edge-rim-light.md",
    "EdgeDetectPRO AG": "filter/edges/edge-detect-pro.md",
    "Erode_Fine SPIN": "filter/edges/erode-fine.md",
    "Edge_Expand SPIN": "filter/edges/edge-expand.md",
    "Edge RB": "filter/edges/edge.md",
    "ColourSmear NKPD": "filter/edges/colour-smear.md",
    "KillOutline NKPD": "filter/edges/kill-outline.md",
    "EdgeFromAlpha FR": "filter/edges/edge-from-alpha.md",
    "VectorExtendEdge NKPD": "filter/edges/vector-extend-edge.md",
    "Glass MJT": "filter/distort/glass.md",
    "HeatWave DB": "filter/distort/heat-wave.md",
    "X_Distort XM": "filter/distort/x-distort.md",
    "X Aton Volumetrics XM": "filter/x-tools/x-aton.md",
    "X_Denoise XM": "filter/x-tools/x-denoise.md",
    "X_Sharpen XM": "filter/x-tools/x-sharpen.md",
    "X_Soften XM": "filter/x-tools/x-soften.md",
    "BeautifulSkin NKPD": "filter/beautiful-skin.md",
    "BlacksExpon TL": "filter/blacks-expon.md",
    "Halation NKPD": "filter/halation.md",
    "Highpass NKPD": "filter/highpass.md",
    "Diffusion NKPD": "filter/diffusion.md",
    "LightWrapPro TL": "filter/lightwrap-pro.md",
    "bm_Lightwrap BM": "filter/bm-lightwrap.md",
    "iConvolve NKPD": "filter/iconvolve.md",
    "ConvolutionMatrix NKPD": "filter/convolution-matrix.md",
    "apChroma AP": "filter/apchroma.md",
    "apChromaTransform AP": "filter/apchroma-transform.md",
    "apChromaBlur AP": "filter/apchroma-blur.md",
    "apChromaUnpremult AP": "filter/apchroma-unpremult.md",
    "apChromaPremult AP": "filter/apchroma-premult.md",
    "apChromaMerge AP": "filter/apchroma-merge.md",
    "Chromatik NKPD": "filter/chromatik.md",
    "CatsEyeDefocus NKPD": "filter/cats-eye-defocus.md",
    "DefocusSwirlyBokeh NKPD": "filter/defocus-swirly-bokeh.md",
    "deHaze MJT": "filter/dehaze.md",
    "RankFilter NKPD": "filter/rank-filter.md",
    "DeflickerVelocity NKPD": "filter/deflicker-velocity.md",
    "FillSampler NKPD": "filter/fill-sampler.md",
    "MECfiller NKPD": "filter/mec-filler.md",
    "apDespill AP": "keyer/ap-despill.md",
    "SpillCorrect NKPD": "keyer/spill-correct.md",
    "DespillToColor NKPD": "keyer/despill-to-color.md",
    "AdditiveKeyerPro TL": "keyer/additive-keyer-pro.md",
    "apeScreenClean AP": "keyer/ape-screen-clean.md",
    "apScreenGrow AP": "keyer/ap-screen-grow.md",
    "KeyChew NKPD": "keyer/key-chew.md",
    "LumaKeyer NKPD": "keyer/luma-keyer.md",
    "ContactSheetAuto TL": "merge/contact-sheet-auto.md",
    "KeymixBBox TL": "merge/keymix-bbox.md",
    "MergeAtmos TL": "merge/merge-atmos.md",
    "MergeBlend TL": "merge/merge-blend.md",
    "MergeAll NKPD": "merge/merge-all.md",
    "VectorMathTools TL": "transform/vector-math-tools.md",
    "VectorTracker NKPD": "transform/vector-tracker.md",
    "AutoCropTool NKPD": "transform/auto-crop-tool.md",
    "BBoxToFormat NKPD": "transform/bbox-to-format.md",
    "ImagePlane3D NKPD": "transform/image-plane-3d.md",
    "Matrix4x4_Inverse TL": "transform/matrix4x4-inverse.md",
    "Matrix4x4_Math TL": "transform/matrix4x4-math.md",
    "MirrorBorder TL": "transform/mirror-border.md",
    "TransformCutOut NKPD": "transform/transform-cut-out.md",
    "iMorph NKPD": "transform/imorph.md",
    "RP_Reformat NKPD": "transform/rp-reformat.md",
    "InverseMatrix33 MT": "transform/inverse-matrix33.md",
    "InverseMatrix44 MT": "transform/inverse-matrix44.md",
    "CardToTrack NKPD": "transform/card-to-track.md",
    "CProject MJT": "transform/cproject.md",
    "TProject MJT": "transform/tproject.md",
    "STiCKiT NKPD": "transform/stickit.md",
    "TransformMatrix TL": "transform/transform-matrix.md",
    "CornerPin2D_Matrix TL": "transform/cornerpin2d-matrix.md",
    "IIDistort NKPD": "transform/iidistort.md",
    "CameraShake NKPD": "transform/camera-shake.md",
    "MorphDissolve SPIN": "transform/morph-dissolve.md",
    "ITransform NKPD": "transform/itransform.md",
    "RotoCentroid NKPD": "transform/roto-centroid.md",
    "STMapInverse MT": "transform/stmap-inverse.md",
    "GenerateSTMap MT": "transform/stmap-inverse.md",
    "Transform_Mix FL": "transform/transform-mix.md",
    "PlanarProjection NKPD": "transform/planar-projection.md",
    "Reconcile3DFast NKPD": "transform/reconcile3d-fast.md",
    "aPCard AP": "3d/ap-card.md",
    "DummyCam TL": "3d/dummy-cam.md",
    "mScatterGeo NKPD": "3d/m-scatter-geo.md",
    "Origami MJT": "3d/origami.md",
    "RayDeepAO NKPD": "3d/ray-deep-ao.md",
    "SceneDepthCalculator NKPD": "3d/scene-depth-calculator.md",
    "SSMesh NKPD": "3d/ss-mesh.md",
    "Unify3DCoordinate NKPD": "3d/unify-3d-coordinate.md",
    "UVEditor MJT": "3d/uv-editor.md",
    "Distance3D MJT": "3d/distance-3d.md",
    "DistanceBetween_CS MJT": "3d/distance-between-cs.md",
    "Lightning3D MJT": "3d/lightning-3d.md",
    "GeoToPoints NKPD": "3d/geo-to-points.md",
    "Noise3DTexture NKPD": "3d/noise-3d-texture.md",
    "GodRaysProjector NKPD": "3d/god-rays-projector.md",
    "WaterSchmutz NKPD": "particles/waterschmutz.md",
    "Sparky NKPD": "particles/sparky.md",
    "RainMaker NKPD": "particles/rainmaker.md",
    "ParticleLights NKPD": "particles/particlelights.md",
    "ParticleKiller NKPD": "particles/particlekiller.md",
    "Deep2VP MJT": "deep/deep2vp.md",
    "DVPmatte MJT": "deep/deep2vp.md",
    "DVPattern MJT": "deep/deep2vp.md",
    "DVPColorCorrect MJT": "deep/deep2vp.md",
    "DVProjection MJT": "deep/deep2vp.md",
    "DVPsetLight MJT": "deep/deep2vp.md",
    "DVPfresnel MJT": "deep/deep2vp.md",
    "DVPrelight MJT": "deep/deep2vp.md",
    "DVPrelightPT MJT": "deep/deep2vp.md",
    "DVPShader MJT": "deep/deep2vp.md",
    "DVPToonShader MJT": "deep/deep2vp.md",
    "DVPscene MJT": "deep/deep2vp.md",
    "DeepFromDepth NKPD": "deep/deepfromdepth.md",
    "DeepToPosition NKPD": "deep/deeptoposition.md",
    "Z2P MJT": "deep/deeptoposition.md",
    "DeepRecolorMatte NKPD": "deep/deeprecolormatte.md",
    "DeepMerge_Advanced TL": "deep/deepmerge-advanced.md",
    "DeepCropSoft NKPD": "deep/deepcropsoft.md",
    "DeepKeyMix NKPD": "deep/deepkeymix.md",
    "DeepHoldoutSmoother NKPD": "deep/deepholdoutsmoother.md",
    "DeepCopyBBox NKPD": "deep/deepcopybbox.md",
    "DeepBoolean NKPD": "deep/deepboolean.md",
    "DeepFromPosition NKPD": "deep/deepfromposition.md",
    "DeepSampleCount NKPD": "deep/deepsamplecount.md",
    "DeepSer NKPD": "deep/deepser.md",
    "UV_Mapper TL": "cg/uv-mapper.md",
    "PNZ Suite MJT": "cg/pnz-suite.md",
    "PosToolkit MJT": "cg/pos-toolkit.md",
    "PosPattern MJT": "cg/pos-toolkit.md",
    "PosProjection MJT": "cg/pos-toolkit.md",
    "Noise3D NKPD": "cg/noise3d.md",
    "Noise4D NKPD": "cg/noise4d.md",
    "Relight_Simple NKPD": "cg/relight-simple.md",
    "Reproject3D NKPD": "cg/reproject3d.md",
    "C44Kernal NKPD": "cg/c44kernal.md",
    "apDirLight AP": "cg/apdirlight.md",
    "apFresnel AP": "cg/apfresnel.md",
    "CameraNormals NKPD": "cg/cameranormals.md",
    "NormalsRotate NKPD": "cg/normalsrotate.md",
    "EnvReflect_BB NKPD": "cg/envreflect-bb.md",
    "Relight_BB NKPD": "cg/relight-bb.md",
    "N_Reflection NKPD": "cg/n-reflection.md",
    "SimpleSSS NKPD": "cg/simplesss.md",
    "aPmatte AP": "cg/apmatte.md",
    "P_Project MJT": "cg/p-project.md",
    "GlueP MJT": "cg/gluep.md",
    "P_Ramp MJT": "cg/p-ramp.md",
    "P_NoiseAdvanced MJT": "cg/p-noiseadvanced.md",
    "WaveGrade FL": "curves/wavemachine.md",
    "WaveRetime FL": "curves/wavemachine.md",
    "WaveMerge FL": "curves/wavemachine.md",
    "WaveMachine FL": "curves/wavemachine.md",
    "Randomizer AG": "curves/randomizer.md",
    "AnimationCurve AG": "curves/animationcurve.md",
    "CurveRemapper NKPD": "curves/curveremapper.md",
    "NoiseGen NKPD": "curves/noisegen.md",
    "GUI_Switch TL": "utilities/gui-switch.md",
    "NAN_INF_Killer TL": "utilities/nan-inf-killer.md",
    "apViewerBlocker AP": "utilities/apviewerblocker.md",
    "Python_and_TCL AG": "utilities/python-and-tcl.md",
    "RotoQC NKPD": "utilities/rotoqc.md",
    "bm_MatteCheck BM": "utilities/bm-mattecheck.md",
    "ViewerRender NKPD": "utilities/viewerrender.md",
    "NukeZ NKPD": "utilities/nukez.md",
    "Pyclopedia NKPD": "utilities/pyclopedia.md",
    "Advanced Keying Template": "workflow-templates/advanced-keying-template.md",
    "Advanced Keying Template Stamps Version": "workflow-templates/advanced-keying-template-stamps.md",
    "STMap Keyer Setup": "workflow-templates/stmap-keyer-setup.md",
}

def main():
    print("=" * 100)
    print("FULL AUDIT: Google Doc vs Markdown Wiki — Image Cross-Reference")
    print("=" * 100)

    rmap = load_rename_map()  # old -> new
    rev_map = load_reverse_map()  # new -> old

    gdoc_sections = parse_gdoc()
    md_images = parse_markdown_images()

    # For each Google Doc section, get expected images (as new names)
    # and compare with what's actually in the markdown

    errors = []
    warnings = []
    ok_count = 0

    # Build: md_file -> set of expected original images (from Google Doc)
    md_expected = defaultdict(set)  # md_path -> set of original image names

    for heading, gdoc_imgs in gdoc_sections.items():
        md_file = GDOC_TO_MD.get(heading)
        if md_file is None:
            if gdoc_imgs:
                warnings.append(f"UNMAPPED SECTION: '{heading}' has {len(gdoc_imgs)} images but no markdown mapping: {gdoc_imgs}")
            continue
        for img in gdoc_imgs:
            md_expected[md_file].add(img)

    # Now compare
    all_md_files = set(list(md_expected.keys()) + list(md_images.keys()))

    for md_file in sorted(all_md_files):
        expected_originals = md_expected.get(md_file, set())
        actual_new_names = md_images.get(md_file, [])

        # Convert actual new names back to original names
        actual_originals = set()
        for new_name in actual_new_names:
            orig = rev_map.get(new_name)
            if orig:
                actual_originals.add(orig)
            else:
                # Might be a non-tool image or not in rename map
                actual_originals.add(f"[{new_name}]")

        # Convert expected originals to new names for readable output
        expected_new = set()
        for orig in expected_originals:
            new = rmap.get(orig, f"[UNKNOWN:{orig}]")
            expected_new.add(new)

        # Compare
        missing = expected_originals - actual_originals
        extra_originals = actual_originals - expected_originals
        # Filter out bracketed entries from extra (those are images without rename map entries)
        extra = {e for e in extra_originals if not e.startswith('[')}

        if missing or extra:
            missing_new = [rmap.get(m, m) for m in missing]
            extra_new = [rmap.get(e, e) for e in extra]

            entry = f"\n{'!'*3} {md_file}"
            if missing:
                entry += f"\n    MISSING from wiki (in Google Doc): {sorted(missing)} -> {sorted(missing_new)}"
            if extra:
                entry += f"\n    EXTRA in wiki (not in Google Doc for this tool): {sorted(extra)} -> {sorted(extra_new)}"
                # Find where the extra image SHOULD be
                for e in sorted(extra):
                    for heading, imgs in gdoc_sections.items():
                        if e in imgs:
                            correct_md = GDOC_TO_MD.get(heading, "UNMAPPED")
                            entry += f"\n      -> {e} ({rmap.get(e,e)}) belongs to '{heading}' -> {correct_md}"
            errors.append(entry)
        else:
            ok_count += 1

    # Print results
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}")
    print(f"\nPages checked: {len(all_md_files)}")
    print(f"Pages OK (images match): {ok_count}")
    print(f"Pages with errors: {len(errors)}")
    print(f"Warnings (unmapped sections): {len(warnings)}")

    if errors:
        print(f"\n{'='*80}")
        print("ERRORS — Image mismatches:")
        print(f"{'='*80}")
        for e in errors:
            print(e)

    if warnings:
        print(f"\n{'='*80}")
        print("WARNINGS — Unmapped Google Doc sections:")
        print(f"{'='*80}")
        for w in warnings:
            print(f"  {w}")

    if not errors and not warnings:
        print("\n*** ALL CLEAR — Every page matches the Google Doc! ***")

if __name__ == "__main__":
    main()
