import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// VPython 스타일 3D 씬을 관리하는 렌더러.
// Python(Pyodide) 쪽에서는 globalThis.vpw 를 통해 createObject/updateObject 를 호출한다.
export class Renderer {
  constructor(container) {
    this.container = container;
    this.objects = new Map();
    this.nextId = 1;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000000);

    this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
    this.camera.position.set(0, 3, 12);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;

    // VPython 기본 조명과 유사하게: 은은한 환경광 + 방향광 2개
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const d1 = new THREE.DirectionalLight(0xffffff, 1.6);
    d1.position.set(4, 6, 8);
    this.scene.add(d1);
    const d2 = new THREE.DirectionalLight(0xffffff, 0.6);
    d2.position.set(-4, -2, -6);
    this.scene.add(d2);

    this._resize = this._resize.bind(this);
    new ResizeObserver(this._resize).observe(container);
    this._resize();

    const animate = () => {
      requestAnimationFrame(animate);
      this.controls.update();
      this.renderer.render(this.scene, this.camera);
    };
    animate();
  }

  _resize() {
    const w = this.container.clientWidth || 1;
    const h = this.container.clientHeight || 1;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  // type: 'box' | 'sphere', propsJson: JSON 문자열 (Python에서 직렬화해서 전달)
  createObject(type, propsJson) {
    const props = JSON.parse(propsJson);
    let geometry;
    if (type === 'box') {
      geometry = new THREE.BoxGeometry(1, 1, 1);
    } else if (type === 'sphere') {
      geometry = new THREE.SphereGeometry(1, 48, 32);
    } else {
      throw new Error(`unknown object type: ${type}`);
    }
    const material = new THREE.MeshStandardMaterial({ roughness: 0.5, metalness: 0.0 });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.userData.type = type;

    const id = this.nextId++;
    this.objects.set(id, mesh);
    this.scene.add(mesh);
    this._applyProps(mesh, props);
    return id;
  }

  updateObject(id, propsJson) {
    const mesh = this.objects.get(id);
    if (!mesh) return; // 이전 실행에서 남은 오래된 참조는 무시
    this._applyProps(mesh, JSON.parse(propsJson));
  }

  _applyProps(mesh, props) {
    if (props.pos) mesh.position.set(props.pos[0], props.pos[1], props.pos[2]);
    if (props.color) mesh.material.color.setRGB(props.color[0], props.color[1], props.color[2]);
    if (props.size) mesh.scale.set(props.size[0], props.size[1], props.size[2]);
    if (props.radius !== undefined) mesh.scale.setScalar(props.radius);
    if (props.opacity !== undefined) {
      mesh.material.transparent = props.opacity < 1;
      mesh.material.opacity = props.opacity;
    }
    if (props.visible !== undefined) mesh.visible = props.visible;
  }

  // 새 실행 전에 이전 실행의 오브젝트를 모두 제거
  reset() {
    for (const mesh of this.objects.values()) {
      this.scene.remove(mesh);
      mesh.geometry.dispose();
      mesh.material.dispose();
    }
    this.objects.clear();
  }
}
