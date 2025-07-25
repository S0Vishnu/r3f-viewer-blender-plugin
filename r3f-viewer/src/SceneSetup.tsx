import { useEffect, useState } from "react";
import { PerspectiveCamera } from "@react-three/drei";

type CameraConfig = {
  name: string;
  type: string;
  fov: number;
  position: [number, number, number];
  rotation: [number, number, number];
};

type LightConfig = {
  name: string;
  type: string;
  color: [number, number, number];
  intensity: number;
  position: [number, number, number];
  angle?: number;
  target?: [number, number, number];
};

type SceneData = {
  cameras: CameraConfig[];
  lights: LightConfig[];
  background: [number, number, number];
};

export function SceneSetup() {
  const [config, setConfig] = useState<SceneData | null>(null);

  useEffect(() => {
    fetch("/lights_and_cameras.json")
      .then((res) => res.json())
      .then(setConfig);
  }, []);

  if (!config) return null;

  return (
    <>
      {/* Background */}
      <color attach="background" args={[`rgb(${config.background.map(c => c * 255).join(",")})`]} />

      {/* Cameras */}
      {config.cameras.map((cam, i) => (
        <PerspectiveCamera
          key={i}
          makeDefault={i === 0}
          fov={cam.fov}
          position={cam.position}
          rotation={cam.rotation}
        />
      ))}

      {/* Lights */}
      {config.lights.map((light, i) => {
        const common = {
          key: i,
          color: light.color,
          intensity: light.intensity,
          position: light.position,
        };

        switch (light.type) {
          case "POINT":
            return <pointLight {...common} />;
          case "SPOT":
            return (
              <spotLight
                {...common}
                angle={light.angle ?? 0.3}
                target-position={light.target}
              />
            );
          case "AREA":
            return <rectAreaLight {...common} />;
          default:
            return null;
        }
      })}
    </>
  );
}
