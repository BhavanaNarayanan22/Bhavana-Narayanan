from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates


from .schemas import PromptRequest

from .services.gemini_flash import (
    generate_outline
)

from .services.gemini_pro import (
    generate_story
)

from .services.image_generator import (
    generate_image
)

from .services.layout_builder import (
    build_comic_layout
)

from .services.exporters import (
    save_pdf
)


router = APIRouter()


templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# --------------------------------------------------
# MAIN COMIC GENERATION PIPELINE
# --------------------------------------------------

async def generate_comic(
    prompt: PromptRequest
):

    # Step 1
    # Generate five-panel outline
    outline = generate_outline(
        story_prompt=prompt.story_prompt,
        character_name=prompt.character_name,
        setting=prompt.setting,
        tone=prompt.tone,
        art_style=prompt.art_style
    )


    # Step 2
    # Generate narration and dialogue
    story = generate_story(
        outline
    )


    # Step 3
    # Generate images
    image_paths = []

    for panel in outline:

        image_path = generate_image(
            image_prompt=panel["image_prompt"],
            panel_number=panel["panel_number"]
        )

        image_paths.append(
            image_path
        )


    # Step 4
    # Build final layout
    layout = build_comic_layout(
        outline=outline,
        story=story,
        image_paths=image_paths
    )


    # Step 5
    # Export PDF
    pdf_path = save_pdf(
        layout
    )


    return layout, pdf_path


# --------------------------------------------------
# FORM GENERATION ROUTE
# --------------------------------------------------

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    try:

        prompt = PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style
        )


        layout, pdf_path = await generate_comic(
            prompt
        )


        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,

                "layout": layout,

                "pdf_path": pdf_path
            }
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# --------------------------------------------------
# JSON API
# --------------------------------------------------

@router.post(
    "/generate-comic/json"
)
async def generate_json(
    prompt: PromptRequest
):

    try:

        layout, pdf_path = await generate_comic(
            prompt
        )


        return {
            "success": True,
            "layout": layout,
            "pdf_path": pdf_path
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# --------------------------------------------------
# EXPORT SUCCESS
# --------------------------------------------------

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(

    request: Request,

    pdf_path: str = ""
):

    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
            "pdf_path": pdf_path
        }
    )


# --------------------------------------------------
# IMAGE TEST ROUTE
# --------------------------------------------------

@router.get(
    "/test-image",
    response_class=HTMLResponse
)
async def test_image(

    request: Request,

    prompt: str = (
        "A brave fox exploring "
        "an enchanted forest, "
        "comic book style"
    )
):

    try:

        image_path = generate_image(
            image_prompt=prompt,
            panel_number=0
        )


        return templates.TemplateResponse(
            "test_image.html",
            {
                "request": request,

                "image_path": image_path,

                "prompt": prompt
            }
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )