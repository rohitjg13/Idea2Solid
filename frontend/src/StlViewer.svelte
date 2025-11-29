<script>
  import { onMount, onDestroy, createEventDispatcher } from "svelte";
  import * as THREE from "three";
  import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

  export let url;

  const dispatch = createEventDispatcher();
  let container;
  let renderer, scene, camera, controls, animationId;

  onMount(() => {
    if (!url) return;
    init();
    loadSTL(url);
    animate();
  });

  onDestroy(() => {
    if (animationId) cancelAnimationFrame(animationId);
    if (renderer) renderer.dispose();
    if (controls) controls.dispose();
  });

  function init() {
    const width = container.clientWidth;
    const height = container.clientHeight;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000); // Pitch black

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1);
    dirLight.position.set(10, 10, 10);
    scene.add(dirLight);
    
    const backLight = new THREE.DirectionalLight(0xffffff, 0.5);
    backLight.position.set(-10, -10, -10);
    scene.add(backLight);

    // Camera
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(50, 50, 50);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.enableZoom = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 2.0;

    // Grid
    const gridHelper = new THREE.GridHelper(200, 20, 0xffffff, 0x333333);
    scene.add(gridHelper);
    
    // Axes
    const axesHelper = new THREE.AxesHelper(10);
    scene.add(axesHelper);

    window.addEventListener("resize", onWindowResize);
  }

  function loadSTL(stlUrl) {
    const loader = new STLLoader();
    loader.load(
      stlUrl,
      (geometry) => {
        const material = new THREE.MeshPhongMaterial({
          color: 0xffffff,
          specular: 0x111111,
          shininess: 200,
        });
        const mesh = new THREE.Mesh(geometry, material);

        // Center geometry
        geometry.computeBoundingBox();
        geometry.center();
        
        // Adjust camera based on size
        const box = geometry.boundingBox;
        const size = new THREE.Vector3();
        box.getSize(size);

        dispatch('dimensions', {
          x: size.x,
          y: size.y,
          z: size.z
        });

        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
        cameraZ *= 2.5; // Zoom out a bit
        camera.position.set(cameraZ, cameraZ * 0.6, cameraZ);
        camera.lookAt(0, 0, 0);

        mesh.rotation.x = -Math.PI / 2; // OpenSCAD Z-up to Three.js Y-up usually needs rotation, but let's see. 
        // Actually OpenSCAD is Z-up. Three.js is Y-up. 
        // Usually STLs from OpenSCAD come in with Z as up.
        // Rotating -90 deg around X aligns Z to Y.
        mesh.rotation.x = -Math.PI / 2;

        scene.add(mesh);
      },
      (xhr) => {
        // console.log((xhr.loaded / xhr.total) * 100 + "% loaded");
      },
      (error) => {
        console.error("An error happened loading STL", error);
      }
    );
  }

  function onWindowResize() {
    if (!camera || !renderer || !container) return;
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  function animate() {
    animationId = requestAnimationFrame(animate);
    if (controls) controls.update();
    if (renderer && scene && camera) renderer.render(scene, camera);
  }
</script>

<div class="viewer-container" bind:this={container}></div>

<style>
  .viewer-container {
    width: 100%;
    height: 100%;
    min-height: 400px;
    background: #000;
    border-radius: 0;
    overflow: hidden;
  }
</style>
