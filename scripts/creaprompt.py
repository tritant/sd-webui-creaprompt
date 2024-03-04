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
    
#def auto_send_to_final(randprompt):
#    return randprompt
    
def read_random_line_from_csv_files(checkbox_group):
    chosen_lines = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines:
                    random_line = random.choice(lines).strip()
                    for choice in checkbox_group:
                        if choice == filename[3:-4]:
                            chosen_lines.append(random_line)
    concatenated_lines = ",".join(chosen_lines)

    if not any(checkbox_group):
        concatenated_lines = "Please, select a category."
    return concatenated_lines
    
def select_random_line_from_collection():
    file_path = os.path.join(folder_path, "collection.txt")
    if os.path.exists(file_path) and file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            readline = random.choice(lines).strip()
            if lines:
                return readline
            else:
                return "The file is empty."
    else:
        return "The specified file does not exist or is not a text file."    
        
def getfilename():
    name = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
           name.append(filename[3:-4])
    return name
    
def get_config_files():
    config_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".config"):
            config_files.append(filename[:-7])
    return config_files
    
def load_checkbox_state(selected_file):
    if not selected_file:
        print("Please select a file.")
        return
    file_path = os.path.join(folder_path, selected_file + ".config")
    with open(file_path, "r") as file:
        lines = file.readlines()
        selected_checkboxes = [line.strip() for line in lines]
    return selected_checkboxes
    
def save_checkbox_state(checkbox_group, file_name):
                if not file_name:
                  print("Please enter a file name.")
                  return gr.update(choices=get_config_files())
                if not file_name.endswith('.config'):
                  file_name += '.config'
                  file_path = os.path.join(folder_path, file_name)
                with open(file_path, "w") as file:
                  for checkbox in checkbox_group:
                    file.write(f"{checkbox}\n")
                print("Checkbox state saved successfully.")
                return gr.update(choices=get_config_files(), value= file_name[:-7]) 

def uncheck_auto_box(is_collection_enabled, is_enabled ):
    if not is_collection_enabled and not is_enabled:
      return
    return not is_collection_enabled
    
def uncheck_auto_collection(is_enabled, is_collection_enabled):
    if not is_collection_enabled and not is_enabled:
       return
    return not is_enabled

def active_random_prompt(is_enabled, is_collection_enabled):
    if is_enabled or is_collection_enabled:
       return gr.update(interactive=True)
    return gr.update(interactive=False, value=False)
        
checkboxes = getfilename()          

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
              gr.Markdown("# Auto prompting")
              gr.Markdown("When activated, just press the normal generate button, it also works with batch")
              with gr.Row():
                      is_enabled = grc.Checkbox(label="Enable auto prompting", info="Enable auto prompting from selected categories", value=False)
                      is_collection_enabled = grc.Checkbox(label="Enable auto collection", info="Enable auto prompting from collection", value=False)
                      is_randomize = grc.Checkbox(label="Enable random prompts", info="Enable random prompts for each images in batch", value=False, interactive=False)  
              with gr.Row():
                      gr.Markdown("# ")
              with gr.Row():        
                      gr.Markdown("# ")
              with gr.Row():        
                      save_state_button = gr.Button("Save a preset of the selected categories", elem_id="save_state", variant="primary")
                      file_name_textbox = grc.Textbox(elem_id="file_name", show_label=False, placeholder="Enter the name of the preset you want to save", container=True)
                      file_dropdown_component = gr.Dropdown(show_label=False, choices=get_config_files(), elem_id="file_dropdown", value="Select a categories preset")
              with gr.Column():
                      gr.Markdown("#")
                      checkbox_group = grc.CheckboxGroup(label="Select Categories:", choices=checkboxes, default=['base'], min_width=50)
              with gr.Column(scale=3):
                      gr.Markdown("# Create prompt manually")
                      gr.Markdown("Press the normal generate button to start generating image with the final prompt")
                      final = grc.Textbox(label="Final prompt which will be used to generate the image:", elem_id="creaprompt_prompt_final", show_label=True, lines=2, placeholder="The final prompt is displayed here", container=True)
                      CreaPromptScript.final_element = final
                      Prefix = grc.Textbox(label="Prefix of the Prompt:", elem_id="promptgen_prompt_prefix", show_label=True, lines=2, placeholder="Type your prefix or leave blank if you don't want it", container=True)
                      sufix = grc.Textbox(label="Suffix of the Prompt:", elem_id="promptgen_prompt_sufix", show_label=True, lines=2, placeholder="Type your suffix or leave blank if you don't want it", container=True)
                      prompt = grc.Textbox(label="Created Prompt from categories:", elem_id="promptgen_prompt", show_label=True, lines=2, placeholder="Make the selection of your choice and Click Generate button", container=True)
                      gr.Markdown("# ")
                      with gr.Row():
                            Sendbefore = gr.Button('Add before final prompt', elem_id="promptgen_sendto_img", variant='primary')
                            send_text_button = gr.Button(value='Replace final prompt', variant='primary')
                            Sendafter = gr.Button('Add after final prompt', elem_id="promptgen_sendto_txt", variant='primary')                            
                      with gr.Column(scale=1):
                            gr.Markdown("#")
                            with gr.Row():
                                submit = gr.Button('Create prompt from categories', elem_id="promptgen_generate", variant='primary')
                            with gr.Row():
                                gr.Markdown("# ")
                                    
        with contextlib.suppress(AttributeError):
   
            save_state_button.click(save_checkbox_state, inputs= [checkbox_group, file_name_textbox], outputs=[file_dropdown_component])                        
            file_dropdown_component.change(load_checkbox_state, inputs=[file_dropdown_component], outputs=[checkbox_group])
            is_collection_enabled.select(uncheck_auto_box, inputs=[is_collection_enabled, is_enabled], outputs=[is_enabled])
            is_enabled.select(uncheck_auto_collection, inputs=[is_enabled, is_collection_enabled], outputs=[is_collection_enabled])
            is_enabled.select(active_random_prompt, inputs=[is_enabled, is_collection_enabled], outputs=[is_randomize])
            is_collection_enabled.select(active_random_prompt, inputs=[is_enabled, is_collection_enabled], outputs=[is_randomize])
     
            if is_img2img:
                
                submit.click(
                           fn=read_random_line_from_csv_files,
                           inputs=checkbox_group,
                           outputs=prompt
                          )        
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxxIMG], outputs=[self.boxxIMG])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxxIMG], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxxIMG], outputs=[self.boxxIMG])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxxIMG], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxxIMG, Prefix, sufix], outputs=[self.boxxIMG])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxxIMG, Prefix, sufix], outputs=[final])
            else:
                
                submit.click(
                           fn=read_random_line_from_csv_files,
                           inputs=checkbox_group,
                           outputs=prompt
                          )        
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[self.boxx])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[final])
        return [is_enabled, Prefix, sufix, checkbox_group, is_randomize, is_collection_enabled]
        
    def process(self, p, is_enabled, prefix, sufix, checkbox_group, is_randomize, is_collection_enabled):
    
        batchCount = len(p.all_prompts)
    
        if is_collection_enabled:
           if(batchCount == 1):
              for i, prompt in enumerate(p.all_prompts):
              
                  randprompt=select_random_line_from_collection()  
              p.all_prompts[i] = randprompt
              print("Prompt used from collection:" + " " + randprompt)        

           if(batchCount > 1):
            randprompts = {}
            randprompt = ""
            for i, prompt in enumerate(p.all_prompts):
                if(is_randomize):
                   randprompt = select_random_line_from_collection()
                   randprompts[i] = randprompt
                   p.all_prompts[i] = randprompts[i]
                   print("Prompt used from collection:" + " " + randprompts[i])
                else:
                    if i == 0:
                      randprompt = select_random_line_from_collection()
                      print("Prompt used from collection:" + " " + randprompt)
                p.all_prompts[i] = randprompt    
    
        if not is_enabled:
            return

        if(batchCount == 1):
            for i, prompt in enumerate(p.all_prompts):
                randprompt= read_random_line_from_csv_files(checkbox_group)
                if prefix:
                   randprompt = prefix + "," + randprompt
                if sufix:
                   randprompt = randprompt + "," + sufix
            p.all_prompts[i] = randprompt
            print("Prompt used for auto prompting:" + " " + randprompt)
            
        if(batchCount > 1):
            randprompts = {}
            randprompt = ""
            for i, prompt in enumerate(p.all_prompts):
                if(is_randomize):
                   randprompt = read_random_line_from_csv_files(checkbox_group)
                   if prefix:
                      randprompt = prefix + "," + randprompt
                   if sufix:
                      randprompt = randprompt + "," + sufix
                   randprompts[i] = randprompt
                   p.all_prompts[i] = randprompts[i]
                   print("Prompt used for auto prompting:" + " " + randprompts[i])
                else:
                    if i == 0:
                      randprompt = read_random_line_from_csv_files(checkbox_group)
                      if prefix:
                         randprompt = prefix + "," + randprompt
                      if sufix:
                         randprompt = randprompt + "," + sufix
                      print("Prompt used for auto prompting:" + " " + randprompt)
                p.all_prompts[i] = randprompt
        

    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component









