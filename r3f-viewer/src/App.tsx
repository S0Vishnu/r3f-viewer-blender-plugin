import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF } from "@react-three/drei";
import { SceneSetup } from "./SceneSetup";
import { useEffect, useState, Suspense } from "react";

function Meshes() {
  const [files, setFiles] = useState<string[]>([]);

  useEffect(() => {
    fetch("/exported_gltfs/scene.json")
      .then((res) => res.json())
      .then(setFiles);
  }, []);

  useEffect(() => {
    fetch("/exported_gltfs/scene.json")
      .then((res) => res.json())
      .then((files) => {
        files.forEach((file: any) =>
          useGLTF.preload(`/exported_gltfs/${file}`)
        );
        setFiles(files);
      });
  }, []);

  return (
    <>
      {files.map((file) => {
        const url = `/exported_gltfs/${file}`;
        const { scene } = useGLTF(url);
        return <primitive key={file} object={scene} />;
      })}
    </>
  );
}

export default function App() {
  return (
    <Canvas shadows>
      <Suspense fallback={null}>
        <SceneSetup />
        <Meshes />
        <Environment preset="sunset" />
      </Suspense>
      <OrbitControls />
    </Canvas>
  );
}
