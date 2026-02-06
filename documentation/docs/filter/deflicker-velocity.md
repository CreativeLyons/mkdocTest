# DeflickerVelocity NKPD

**Author:** Julien Vanhoenacker

![deflicker-velocity-2.webp](../img/tools/filter/deflicker-velocity-2.webp)

Part of the CG artist's job is to balance rendering time and quality. Low rendering quality often resulting in aliasing, or flickering, specially on raytrace renderers. To find the right balance means to test render with different settings in order to find the one that render the fastest while still being acceptable in terms of aliasing and flickering. But this is time consuming and the render time necessary to achieve this result might also be quite high. It is therefore interesting to find tricks to improve quality with equal or even lower render times. It is possible to use built-in denoisers, however this becomes useless if the flickering happens on the edges of the objects, or if it is on wide GI artefacts (as in lightcache or irradiance GI), and tends to make the image blurry. The technique we present here is deflickering based on previous and next frames.

<video autoplay loop muted playsinline style="width:100%">
  <source src="../img/tools/filter/deflicker-velocity-1.mp4" type="video/mp4">
</video>
