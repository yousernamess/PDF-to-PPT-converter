
import os
from dotenv import load_dotenv
from mpxpy.mathpix_client import MathpixClient

load_dotenv()

client = MathpixClient(
    app_id=os.getenv("app_id"),
    app_key=os.getenv("app_key"),
    # Optional "api_url" argument sets the base URL. This can be useful for development with on-premise deployments
    improve_mathpix = False
)


pdf = client.pdf_new(
    file_path='test questions.pdf',
    convert_to_md=True,

)

# Get the Markdown outputs
md_output_path = pdf.to_md_file(path='output/sample.md')

