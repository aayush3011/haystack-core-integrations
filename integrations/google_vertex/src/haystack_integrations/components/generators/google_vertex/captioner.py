import logging
from typing import Any, Dict, List, Optional

import vertexai
from haystack.core.component import component
from haystack.core.serialization import default_from_dict, default_to_dict
from haystack.dataclasses.byte_stream import ByteStream
from vertexai.vision_models import Image, ImageTextModel

logger = logging.getLogger(__name__)


@component
class VertexAIImageCaptioner:
    """
    `VertexAIImageCaptioner` enables text generation using Google Vertex AI imagetext generative model.

    Authenticates using Google Cloud Application Default Credentials (ADCs).
    For more information see the official [Google documentation](https://cloud.google.com/docs/authentication/provide-credentials-adc).

    Usage example:
    ```python
    import requests

    from haystack.dataclasses.byte_stream import ByteStream
    from haystack_integrations.components.generators.google_vertex import VertexAIImageCaptioner

    captioner = VertexAIImageCaptioner()

    image = ByteStream(
        data=requests.get(
            "https://raw.githubusercontent.com/deepset-ai/haystack-core-integrations/main/integrations/google_vertex/example_assets/robot1.jpg"
        ).content
    )
    result = captioner.run(image=image)

    for caption in result["captions"]:
        print(caption)

    >>> two gold robots are standing next to each other in the desert
    ```
    """

    def __init__(
        self, *, model: str = "imagetext", project_id: Optional[str] = None, location: Optional[str] = None, **kwargs
    ):
        """
        Generate image captions using a Google Vertex AI model.

        Authenticates using Google Cloud Application Default Credentials (ADCs).
        For more information see the official [Google documentation](https://cloud.google.com/docs/authentication/provide-credentials-adc).

        :param project_id: ID of the GCP project to use. By default, it is set during Google Cloud authentication.
        :param model: Name of the model to use.
        :param location: The default location to use when making API calls, if not set uses us-central-1.
            Defaults to None.
        :param kwargs: Additional keyword arguments to pass to the model.
            For a list of supported arguments see the `ImageTextModel.get_captions()` documentation.
        """

        # Login to GCP. This will fail if user has not set up their gcloud SDK
        vertexai.init(project=project_id, location=location)

        self._model_name = model
        self._project_id = project_id
        self._location = location
        self._kwargs = kwargs

        self._model = ImageTextModel.from_pretrained(self._model_name)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self, model=self._model_name, project_id=self._project_id, location=self._location, **self._kwargs
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VertexAIImageCaptioner":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
           Deserialized component.
        """
        return default_from_dict(cls, data)

    @component.output_types(captions=List[str])
    def run(self, image: ByteStream):
        """Prompts the model to generate captions for the given image.

        :param image: The image to generate captions for.
        :returns: A dictionary with the following keys:
            - `captions`: A list of captions generated by the model.
        """
        captions = self._model.get_captions(image=Image(image.data), **self._kwargs)
        return {"captions": captions}
