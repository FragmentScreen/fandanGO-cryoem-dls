"""
SmartEM Client wrapper for FandanGO plugin

This module provides a simplified interface to the SmartEM API
for extracting cryo-EM metadata from DLS systems.
"""

import json
import logging
from typing import Dict, Any, List

# Import from smartem-decisions if available
try:
    from smartem_backend.api_client import SmartEMAPIClient
except ImportError:
    SmartEMAPIClient = None
    logging.warning("smartem_backend not available. Install smartem-decisions package.")


class FandanGOSmartEMClient:
    """
    Wrapper around SmartEMAPIClient for FandanGO integration.

    Provides simplified methods for extracting metadata that will
    be sent to ARIA.
    """

    def __init__(self, base_url: str):
        """
        Initialize the client

        Args:
            base_url: Base URL of the SmartEM API (e.g., "http://localhost:8000")
        """
        if SmartEMAPIClient is None:
            raise ImportError(
                "SmartEMAPIClient not available. "
                "Please install smartem-decisions package or add it to PYTHONPATH"
            )

        self.client = SmartEMAPIClient(base_url=base_url)
        self.logger = logging.getLogger(__name__)

    def extract_acquisition_metadata(self, acquisition_uuid: str) -> Dict[str, Any]:
        """
        Extract complete metadata for an acquisition session.

        This fetches all hierarchical data for a given acquisition:
        - Acquisition (session) metadata
        - All grids in the acquisition
        - Grid squares, foil holes, and micrographs
        - Quality metrics and imaging parameters

        Args:
            acquisition_uuid: UUID of the acquisition to extract

        Returns:
            Dictionary containing structured metadata ready for ARIA submission
        """
        self.logger.info(f"Extracting metadata for acquisition {acquisition_uuid}")

        try:
            # Get acquisition data
            acquisition = self.client.get_acquisition(acquisition_uuid)

            # Get all grids for this acquisition
            grids = self.client.get_acquisition_grids(acquisition_uuid)

            metadata = {
                'acquisition': self._serialize_model(acquisition),
                'grids': []
            }

            # For each grid, get detailed data
            for grid in grids:
                grid_data = {
                    'grid_info': self._serialize_model(grid),
                    'grid_squares': [],
                    'atlas': None
                }

                # Get grid squares for this grid
                try:
                    grid_squares = self.client.get_grid_squares_for_grid(grid.uuid)

                    for gs in grid_squares:
                        gs_data = {
                            'grid_square_info': self._serialize_model(gs),
                            'foil_holes': [],
                            'quality_prediction': None
                        }

                        # Get foil holes for this grid square
                        try:
                            foil_holes = self.client.get_foil_holes_for_gridsquare(gs.uuid)
                            for fh in foil_holes:
                                fh_data = {
                                    'foil_hole_info': self._serialize_model(fh),
                                    'micrographs': []
                                }

                                # Get micrographs for this foil hole
                                try:
                                    micrographs = self.client.get_foil_hole_micrographs(fh.uuid)
                                    fh_data['micrographs'] = [
                                        self._serialize_model(m) for m in micrographs
                                    ]
                                except Exception as e:
                                    self.logger.warning(f"Could not get micrographs for foil hole {fh.uuid}: {e}")

                                gs_data['foil_holes'].append(fh_data)

                        except Exception as e:
                            self.logger.warning(f"Could not get foil holes for grid square {gs.uuid}: {e}")

                        # Get quality prediction for this grid square
                        try:
                            quality = self.client.get_quality_prediction(gs.uuid)
                            if quality:
                                gs_data['quality_prediction'] = self._serialize_model(quality)
                        except Exception as e:
                            self.logger.debug(f"No quality prediction for grid square {gs.uuid}: {e}")

                        grid_data['grid_squares'].append(gs_data)

                except Exception as e:
                    self.logger.warning(f"Could not get grid squares for grid {grid.uuid}: {e}")

                # Get atlas for this grid
                try:
                    atlas = self.client.get_grid_atlas(grid.uuid)
                    if atlas:
                        grid_data['atlas'] = self._serialize_model(atlas)
                except Exception as e:
                    self.logger.debug(f"No atlas for grid {grid.uuid}: {e}")

                metadata['grids'].append(grid_data)

            self.logger.info(f"Successfully extracted metadata for acquisition {acquisition_uuid}")
            return metadata

        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
            raise

    def _serialize_model(self, model) -> Dict[str, Any]:
        """
        Serialize a Pydantic model to JSON-compatible dictionary

        Args:
            model: Pydantic model instance

        Returns:
            JSON-compatible dictionary
        """
        if hasattr(model, 'model_dump'):
            return model.model_dump(mode='json')
        elif hasattr(model, 'dict'):
            return model.dict()
        else:
            return dict(model)

    def get_available_acquisitions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of recent acquisitions

        Args:
            limit: Maximum number of acquisitions to return

        Returns:
            List of acquisition summaries
        """
        acquisitions = self.client.get_acquisitions()

        # Sort by start time (most recent first) and limit
        sorted_acqs = sorted(
            acquisitions,
            key=lambda a: a.start_time if hasattr(a, 'start_time') and a.start_time else '',
            reverse=True
        )[:limit]

        return [self._serialize_model(acq) for acq in sorted_acqs]

    def close(self):
        """Close the client connection"""
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
