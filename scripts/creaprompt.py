import contextlib
import os
import gradio as gr
import random
import pandas as pd
from gradio import components as grc
from modules import scripts
from modules import script_callbacks

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "../csv/" )

def send_text_to_prompt(new_text, old_text, Prefix, sufix):
    if Prefix:
        new_text = Prefix + "," + new_text
    if sufix:
        new_text = new_text + "," + sufix
    return new_text
    
def send_before_prompt(new_text, old_text):
    return new_text + "," + old_text
    
def send_after_prompt(new_text, old_text):
    return old_text + "," + new_text    
    
def read_random_line_from_csv_files(Prefix, sufix, *args):
    chosen_lines = []
    for idx, filename in enumerate(os.listdir(folder_path)):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            if not df.empty:
                random_index = random.randint(0, len(df))
                random_row = df.iloc[random_index - 1]
                for i, arg in enumerate(args):
                    if i == idx and arg:
                       chosen_lines.extend(map(str, random_row.tolist()))
    concatenated_lines = ",".join(chosen_lines)
    

    if not any(args):
        concatenated_lines = "Please, select a category."
    return concatenated_lines

class CreaPromptScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return "CreaPrompt"

    def show(self, is_img2img):
        return scripts.AlwaysVisible
 
    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("CreaPrompt", open=False):
              gr.Markdown("# CreaPrompt")
              gr.Markdown("Select the categories you want to use to create the prompt or build your prompt category by category")
              with gr.Row():
                with gr.Column(scale=10):
                      checkboxes = []
                      for filename in os.listdir(folder_path):
                        if filename.endswith(".csv"):
                          #checkbox = gr.inputs.Checkbox(label=filename[3:-4])
                          checkbox = grc.Checkbox(label=filename[3:-4])
                          checkboxes.append(checkbox) 
                          checkbox_rows = [[checkbox] for checkbox in checkboxes]
                with gr.Column(scale=50):
                      final = grc.Textbox(label="Final prompt which will be used to generate the image:", elem_id="promptgen_prompt_final", show_label=True, lines=2, placeholder="The final prompt is displayed here", container=True)
                      Prefix = grc.Textbox(label="Prefix of the Prompt:", elem_id="promptgen_prompt_prefix", show_label=True, lines=2, placeholder="Type your prefix or leave blank if you don't want it", container=True)
                      sufix = grc.Textbox(label="Suffix of the Prompt:", elem_id="promptgen_prompt_sufix", show_label=True, lines=2, placeholder="Type your suffix or leave blank if you don't want it", container=True)
                      prompt = grc.Textbox(label="Created Prompt from categories:", elem_id="promptgen_prompt", show_label=True, lines=2, placeholder="Make the selection of your choice and Click Generate button", container=True)
                      with gr.Row():
                            gr.Markdown("# Create prompt manually")
                      with gr.Row():      
                            gr.Markdown("Press the normal generate button to start generating image with the final prompt")
                      with gr.Row():
                            Sendbefore = gr.Button('Add before final prompt', elem_id="promptgen_sendto_img", variant='primary')
                            send_text_button = gr.Button(value='Replace final prompt', variant='primary')
                            Sendafter = gr.Button('Add after final prompt', elem_id="promptgen_sendto_txt", variant='primary')                            
                      with gr.Row():
                            submit = gr.Button('Create prompt from categories', elem_id="promptgen_generate", variant='primary')
                
        with contextlib.suppress(AttributeError):
            submit.click(
                           fn=read_random_line_from_csv_files,
                           inputs=[Prefix] + [sufix] + checkboxes,
                           outputs=prompt
                          )        
            if is_img2img:
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxxIMG], outputs=[self.boxxIMG])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxxIMG], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxxIMG], outputs=[self.boxxIMG])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxxIMG], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxxIMG, Prefix, sufix], outputs=[self.boxxIMG])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxxIMG, Prefix, sufix], outputs=[final])
            else:
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[self.boxx])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[final])
        return [prompt, send_text_button]

    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component








