import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import zipfile

st.title("Corte Interativo de Imagens em Lote")

# Upload múltiplo de imagens
uploaded_files = st.file_uploader("Envie as imagens", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Mostrar as imagens enviadas
    st.write(f"{len(uploaded_files)} imagens carregadas.")

    # Selecionar uma imagem de exemplo para definir o corte
    example_image_file = st.selectbox("Escolha a imagem para definir o corte", options=uploaded_files, format_func=lambda x: x.name)

    if example_image_file:
        img = Image.open(example_image_file)
        st.image(img, caption="Imagem selecionada para corte", use_column_width=True)

        # Canvas para desenhar o retângulo de seleção
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 255, 0.3)",  # cor azul translúcida
            stroke_width=2,
            stroke_color="blue",
            background_image=img,
            height=img.height,
            width=img.width,
            drawing_mode="rect",
            key="canvas",
        )

        if canvas_result.json_data is not None:
            # Obter coordenadas do retângulo desenhado
            objects = canvas_result.json_data["objects"]
            if objects:
                obj = objects[0]  # Considera o primeiro retângulo desenhado
                left = int(obj["left"])
                top = int(obj["top"])
                width = int(obj["width"])
                height = int(obj["height"])

                st.write(f"Área selecionada: x={left}, y={top}, largura={width}, altura={height}")

                if st.button("Aplicar corte em todas as imagens"):
                    # Criar zip com as imagens cortadas
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for uploaded_file in uploaded_files:
                            image = Image.open(uploaded_file)
                            cropped = image.crop((left, top, left + width, top + height))

                            # Salvar em bytes para colocar no zip
                            img_byte_arr = io.BytesIO()
                            cropped.save(img_byte_arr, format='JPEG')
                            img_byte_arr = img_byte_arr.getvalue()

                            zip_file.writestr(uploaded_file.name, img_byte_arr)

                    st.success("Corte aplicado em todas as imagens!")
                    st.download_button(
                        label="Baixar todas as imagens cortadas (.zip)",
                        data=zip_buffer.getvalue(),
                        file_name="imagens_cortadas.zip",
                        mime="application/zip"
                    )
