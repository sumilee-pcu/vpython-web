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

  // type: 'box' | 'sphere' | 'cylinder', propsJson: JSON 문자열 (Python에서 직렬화해서 전달)
  createObject(type, propsJson) {
    const props = JSON.parse(propsJson);
    let geometry;
    if (type === 'box') {
      geometry = new THREE.BoxGeometry(1, 1, 1);
    } else if (type === 'sphere') {
      geometry = new THREE.SphereGeometry(1, 48, 32);
    } else if (type === 'cylinder') {
      geometry = new THREE.CylinderGeometry(1, 1, 1, 48);
      // three.js 원기둥은 로컬 Y축 중심 기준이다. VPython cylinder는
      // pos에서 시작해 로컬 +X 방향으로 axis 길이만큼 뻗어야 한다.
      geometry.rotateZ(-Math.PI / 2);
      geometry.translate(0.5, 0, 0);
    } else {
      throw new Error(`unknown object type: ${type}`);
    }
    const material = new THREE.MeshStandardMaterial({ roughness: 0.5, metalness: 0.0 });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.userData.type = type;
    mesh.userData.axis = [1, 0, 0];
    mesh.userData.up = [0, 1, 0];
    mesh.userData.radius = 1;

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

  // 브리지 프로토콜 v2: rate()마다 변경분을 일괄 수신 { "3": {pos:[..]}, "7": {...} }
  applyUpdates(batchJson) {
    const batch = JSON.parse(batchJson);
    for (const id of Object.keys(batch)) {
      const mesh = this.objects.get(Number(id));
      if (!mesh) continue; // 이전 세대 잔여 업데이트는 무시
      this._applyProps(mesh, batch[id]);
    }
  }

  _applyProps(mesh, props) {
    if (props.pos) mesh.position.set(props.pos[0], props.pos[1], props.pos[2]);
    if (props.axis || props.up) {
      if (props.axis) mesh.userData.axis = props.axis;
      if (props.up) mesh.userData.up = props.up;
      this._applyOrientation(mesh);
    }
    if (props.color) mesh.material.color.setRGB(props.color[0], props.color[1], props.color[2]);
    if (props.size) mesh.scale.set(props.size[0], props.size[1], props.size[2]);
    if (props.radius !== undefined) {
      if (mesh.userData.type === 'cylinder') {
        mesh.userData.radius = props.radius;
      } else {
        mesh.scale.setScalar(props.radius);
      }
    }
    if (mesh.userData.type === 'cylinder' && (props.axis || props.radius !== undefined)) {
      this._applyCylinderScale(mesh);
    }
    if (props.opacity !== undefined) {
      mesh.material.transparent = props.opacity < 1;
      mesh.material.opacity = props.opacity;
    }
    if (props.visible !== undefined) mesh.visible = props.visible;
  }

  // VPython 의미론: 객체의 로컬 X축이 axis 방향, up은 로컬 Y축 힌트.
  // 기저(x̂, ŷ, ẑ)를 만들어 쿼터니언으로 적용한다. (ARCHITECTURE.md 참고)
  _applyOrientation(mesh) {
    const x = new THREE.Vector3(...mesh.userData.axis);
    if (x.lengthSq() < 1e-24) x.set(1, 0, 0);
    x.normalize();
    let up = new THREE.Vector3(...mesh.userData.up);
    if (up.lengthSq() < 1e-24) up.set(0, 1, 0);
    let z = new THREE.Vector3().crossVectors(x, up);
    if (z.lengthSq() < 1e-12) {
      // axis ∥ up 폴백: axis가 수직에 가까우면 (0,0,1)을 up으로
      up = Math.abs(x.y) < 0.99 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(0, 0, 1);
      z = new THREE.Vector3().crossVectors(x, up);
    }
    z.normalize();
    const y = new THREE.Vector3().crossVectors(z, x);
    mesh.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
  }

  _applyCylinderScale(mesh) {
    const axis = new THREE.Vector3(...mesh.userData.axis);
    const length = axis.length();
    const radius = mesh.userData.radius;
    mesh.scale.set(length, radius, radius);
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
