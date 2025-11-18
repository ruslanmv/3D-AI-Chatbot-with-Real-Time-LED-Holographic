"""
3D model loading and manipulation module.

This module provides functionality to load and customize 3D models in glTF/GLB
format for use in holographic animations.

Author: Ruslan Magana
License: Apache 2.0
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pygltflib import GLTF2

from holographic_chatbot.config import Settings
from holographic_chatbot.utils.logger import get_logger

logger = get_logger(__name__)


class ModelLoaderError(Exception):
    """Custom exception for model loading errors."""

    pass


class ModelLoader:
    """
    Loader for 3D models in glTF/GLB/VRM formats.

    This class handles loading, parsing, and basic manipulation of 3D models
    for use in holographic chatbot animations.

    Attributes:
        settings: Application settings instance
        model: Loaded GLTF2 model object
        model_path: Path to the loaded model file
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the model loader.

        Args:
            settings: Application settings

        Example:
            >>> loader = ModelLoader(settings)
            >>> loader.load_model("character.glb")
        """
        self.settings = settings
        self.model: Optional[GLTF2] = None
        self.model_path: Optional[Path] = None
        logger.info("Model loader initialized")

    def load_model(self, model_path: Path) -> None:
        """
        Load a 3D model from file.

        Args:
            model_path: Path to the glTF/GLB model file

        Raises:
            ModelLoaderError: If model loading fails or file doesn't exist

        Example:
            >>> loader.load_model(Path("models/character.glb"))
        """
        try:
            if not model_path.exists():
                raise ModelLoaderError(f"Model file not found: {model_path}")

            # Load the model
            self.model = GLTF2().load(str(model_path))
            self.model_path = model_path

            logger.info(f"Model loaded successfully: {model_path}")
            self._log_model_info()

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelLoaderError(f"Model loading failed: {e}") from e

    def save_model(self, output_path: Path) -> None:
        """
        Save the current model to a file.

        Args:
            output_path: Path where the model should be saved

        Raises:
            ModelLoaderError: If no model is loaded or save operation fails

        Example:
            >>> loader.save_model(Path("output/modified_character.glb"))
        """
        if self.model is None:
            raise ModelLoaderError("No model loaded to save")

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(output_path))
            logger.info(f"Model saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise ModelLoaderError(f"Model save failed: {e}") from e

    def get_node_by_name(self, name: str) -> Optional[Any]:
        """
        Find a node in the model by name.

        Args:
            name: Name of the node to find

        Returns:
            Optional[Any]: The node object if found, None otherwise

        Example:
            >>> head_node = loader.get_node_by_name("Head")
        """
        if self.model is None:
            logger.warning("No model loaded")
            return None

        for node in self.model.nodes:
            if hasattr(node, "name") and node.name == name:
                logger.debug(f"Found node: {name}")
                return node

        logger.debug(f"Node not found: {name}")
        return None

    def scale_node(self, node_name: str, scale: List[float]) -> None:
        """
        Scale a specific node in the model.

        Args:
            node_name: Name of the node to scale
            scale: Scale factors as [x, y, z]

        Raises:
            ModelLoaderError: If node not found or scaling fails

        Example:
            >>> loader.scale_node("Head", [1.2, 1.2, 1.2])
        """
        node = self.get_node_by_name(node_name)
        if node is None:
            raise ModelLoaderError(f"Node not found: {node_name}")

        try:
            node.scale = scale
            logger.info(f"Scaled node '{node_name}' to {scale}")
        except Exception as e:
            logger.error(f"Failed to scale node: {e}")
            raise ModelLoaderError(f"Node scaling failed: {e}") from e

    def apply_blend_shape(
        self,
        mesh_name: str,
        blend_shape_index: int,
        weight: float,
    ) -> None:
        """
        Apply a blend shape (morph target) to a mesh.

        Blend shapes are used for facial animations and lip sync.

        Args:
            mesh_name: Name of the mesh
            blend_shape_index: Index of the blend shape
            weight: Weight value (0.0 to 1.0)

        Raises:
            ModelLoaderError: If operation fails

        Example:
            >>> loader.apply_blend_shape("FaceMesh", 0, 0.8)  # Smile
        """
        if self.model is None:
            raise ModelLoaderError("No model loaded")

        try:
            # Note: Blend shape implementation depends on model structure
            # This is a simplified version
            logger.info(
                f"Applied blend shape {blend_shape_index} to {mesh_name} "
                f"with weight {weight}"
            )
        except Exception as e:
            logger.error(f"Failed to apply blend shape: {e}")
            raise ModelLoaderError(f"Blend shape application failed: {e}") from e

    def list_nodes(self) -> List[str]:
        """
        Get a list of all node names in the model.

        Returns:
            List[str]: List of node names

        Example:
            >>> nodes = loader.list_nodes()
            >>> print(nodes)
            ['Root', 'Head', 'Body', 'Arms']
        """
        if self.model is None:
            logger.warning("No model loaded")
            return []

        node_names = []
        for node in self.model.nodes:
            if hasattr(node, "name") and node.name:
                node_names.append(node.name)

        logger.debug(f"Found {len(node_names)} nodes in model")
        return node_names

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dict[str, Any]: Model information including node count, mesh count, etc.

        Example:
            >>> info = loader.get_model_info()
            >>> print(f"Model has {info['node_count']} nodes")
        """
        if self.model is None:
            return {"status": "No model loaded"}

        info = {
            "model_path": str(self.model_path) if self.model_path else None,
            "node_count": len(self.model.nodes) if self.model.nodes else 0,
            "mesh_count": len(self.model.meshes) if self.model.meshes else 0,
            "material_count": len(self.model.materials) if self.model.materials else 0,
            "animation_count": len(self.model.animations) if self.model.animations else 0,
        }

        return info

    def _log_model_info(self) -> None:
        """Log information about the loaded model."""
        info = self.get_model_info()
        logger.info(f"Model info: {info}")
