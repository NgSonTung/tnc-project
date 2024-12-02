from sklearn.manifold import TSNE
import seaborn as sns
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.openai import OpenAIEmbeddingMode
import src.database.mongodb as mongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from gridfs import GridFS
from mongoengine.connection import get_db

max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
mongo.create_db_connection()
fs = GridFS(get_db(), collection="MapItem")


def visualize_embeddings(df, context_item=None, image_name=None, context_base_id=None, user_id=None):
    processed_lines = []
    max_cells = 1

    # Iterate over the columns of the DataFrame
    for col_name in df.columns:
        # Get the column data and limit it to max_cells
        col_data = df[col_name].head(max_cells)

        # Format the column data into the desired format
        formatted_data = f'"{col_name}" : {" , ".join([str(cell) for cell in col_data])}'

        # Add the formatted data to the processed lines list
        processed_lines.append(formatted_data)

    # Join the processed lines into a single string
    result_string = '\n'.join(processed_lines)

    # Print or do further processing with the result string
    model = OpenAIEmbedding(mode=OpenAIEmbeddingMode.SIMILARITY_MODE)
    embeddings = model.get_text_embedding_batch(
        result_string, show_progress=True)
    arr = np.array(embeddings)

    # Create a t-SNE model and transform the data
    tsne = TSNE(n_components=2, perplexity=5, random_state=42,
                init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(arr)

    # Create arbitrary labels for visualization
    num_points = vis_dims.shape[0]
    arbitrary_labels = [f'Label_{i}' for i in range(num_points)]

    # Reduce dimensions to 2D using t-SNE
    tsne = TSNE(n_components=2, random_state=0)
    values_2d = tsne.fit_transform(arr)

    # Create a DataFrame for plotting
    vdf = pd.DataFrame(values_2d, columns=['x', 'y'])
    vdf['labels'] = arbitrary_labels  # Assign arbitrary labels

    # Use seaborn to create a scatterplot with automatic coloring based on 'labels'
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=vdf, x='x', y='y', hue='labels', palette='hsv')

    # Place the legend to the right
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    # plt.show()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_data = img_buffer.getvalue()

    # Close the plot to release memory
    plt.close()

    id_img = fs.put(img_data, name=image_name, userId=user_id,
                    contextBaseId=context_base_id)
    return str(id_img)
