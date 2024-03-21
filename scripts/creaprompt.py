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
notactive = "Not Active"
active = "Active"
dropdowns = []

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
    
def read_random_line_from_csv_files(checkbox_group):
    chosen_lines = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv") and filename[3:-4] in checkbox_group:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines:
                    chosen_lines.append(random.choice(lines).strip())
    concatenated_lines = ",".join(chosen_lines) if chosen_lines else "Please, select a category."
    return concatenated_lines
    
def read_random_line_from_csv_files_auto(checkbox_group_manu):
    chosen_lines = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv") and filename[3:-4] in checkbox_group_manu:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines:
                    chosen_lines.append(random.choice(lines).strip())
    concatenated_lines = ",".join(chosen_lines) if chosen_lines else "Please, select a category."
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

def read_random_line_from_csv_file_manual(dropdown_index):
    chosen_lines = []
    i = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv") and i == dropdown_index:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines:
                    chosen_lines.append(random.choice(lines).strip())
        i += 1
    concatenated_lines = "".join(chosen_lines)
    return concatenated_lines
        
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
                  return gr.update(choices=get_config_files()), gr.update(choices=get_config_files())
                if not file_name.endswith('.config'):
                  file_name += '.config'
                  file_path = os.path.join(folder_path, file_name)
                with open(file_path, "w") as file:
                  for checkbox in checkbox_group:
                    file.write(f"{checkbox}\n")
                print("Checkbox state saved successfully.")
                return gr.update(choices=get_config_files(), value= file_name[:-7]), gr.update(choices=get_config_files()) 
                
def save_checkbox_state_manu(checkbox_group_manu, file_name):
                if not file_name:
                  print("Please enter a file name.")
                  return gr.update(choices=get_config_files()), gr.update(choices=get_config_files())
                if not file_name.endswith('.config'):
                  file_name += '.config'
                  file_path = os.path.join(folder_path, file_name)
                with open(file_path, "w") as file:
                  for checkbox in checkbox_group_manu:
                    file.write(f"{checkbox}\n")
                print("Checkbox state saved successfully.")
                return gr.update(choices=get_config_files(), value= file_name[:-7]), gr.update(choices=get_config_files())

def uncheck_auto_box(is_collection_enabled, is_enabled, is_manual_enabled):
    if not is_collection_enabled and not is_enabled and not is_manual_enabled:
      return None, None
    return not is_collection_enabled, not is_collection_enabled
    
def uncheck_auto_collection(is_enabled, is_collection_enabled, is_manual_enabled):
    if not is_collection_enabled and not is_enabled and not is_manual_enabled:
       return None, None
    return not is_enabled, not is_enabled
    
def uncheck_auto_manual(is_manual_enabled, is_collection_enabled, is_enabled ):
    if not is_collection_enabled and not is_enabled and not is_manual_enabled:
      return None, None
    return not is_manual_enabled, not is_manual_enabled

    
def handle_dropdown_change(selected_value, dropdown_index):
    concatenated_values = ""
    #global dropdowns
    if selected_value == "🎲Random\n":
       i = 0
       for filename in os.listdir(folder_path):
         if filename.endswith(".csv") and i == dropdown_index:
            selected_value = "🎲Random: " + filename[3:-4] + "🎲"
            dropdown_values[dropdown_index] = selected_value
         i += 1
    else:
        if selected_value == "None\n":
           selected_value =""
           dropdown_values[dropdown_index] = selected_value[1:]
        else:
           dropdown_values[dropdown_index] = selected_value[1:]
    for value in dropdown_values:
        if value:
            concatenated_values += value + ","
    concatenated_values = concatenated_values.rstrip(", ")
    #print(concatenated_values)
    return concatenated_values
        
checkboxes = getfilename()          

class CreaPromptScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()
        
    def title(self):
        return "CreaPrompt"

    def show(self, is_img2img):
        return scripts.AlwaysVisible
        
    def ui(self, is_img2img):
        #is_enabled=""
        with gr.Group():
            with gr.Accordion("🎨CreaPrompt : Not Active",open = False) as acc:
              gr.Markdown("""
                            <center><font size="4">
                                🧠CreaPrompt, the toolbox for crazy prompters🧠
                            </font></center><br>
                            """)
              with gr.Accordion("➡️CreaPrompt collection", open=False):
                     #gr.Markdown("# CreaPrompt collection")
                     gr.Markdown("When activated, just press the normal generate button, it also works with batch")
                     with gr.Row():
                       is_collection_enabled = grc.Checkbox(label="♻️Enable auto prompting", info="💬From CreaPrompt collection", value=False)
                       is_randomize_manu = grc.Checkbox(label="🎲Enable random prompts", info="💬For each images in batch", value=False, interactive=True)
              with gr.Accordion("➡️Auto prompting from categories", open=True):
                with gr.Tab("✨Random"):
                     with gr.Column(scale=3):
                       #gr.Markdown("# Auto prompting from categories")
                       gr.Markdown("When activated, select categories and press the normal generate button, it also works with batch")
                     with gr.Row():
                       is_enabled = grc.Checkbox(label="♻️Enable auto prompting", info="💬From selected categories", value=False)
                       is_randomize = grc.Checkbox(label="🎲Enable random prompts", info="💬For each images in batch", value=False, interactive=True)  
                     with gr.Row():
                       gr.Markdown("# ")
                     with gr.Column(scale=3):
                       prefix_auto = grc.Textbox(label="Prefix of the Prompt:", elem_id="auto_prompt_prefix", show_label=True, lines=2, placeholder="Type your prefix or leave blank if you don't want it", container=True)
                       sufix_auto = grc.Textbox(label="Suffix of the Prompt:", elem_id="auto_prompt_sufix", show_label=True, lines=2, placeholder="Type your suffix or leave blank if you don't want it", container=True)
                     with gr.Row():        
                       gr.Markdown("# ")
                     with gr.Column():
                       gr.Markdown("#")
                       checkbox_group = grc.CheckboxGroup(label="Select Categories:", choices=checkboxes, default=['base'], min_width=50)
                     with gr.Row():
                       gr.Markdown("#")    
                     with gr.Row():                      
                       save_state_button = gr.Button("Save your preset categories", elem_id="save_state", variant="primary")
                       file_name_textbox = grc.Textbox(elem_id="file_name", show_label=False, placeholder="Enter your preset name", container=True)
                       file_dropdown_component = gr.Dropdown(show_label=False, choices=get_config_files(), elem_id="file_dropdown", value="Select a preset")
                with gr.Tab("✨Manual"):
                    gr.Markdown("""
                            <center><font size="4">
                                Work in progress
                            </font><font size="2">To do, save preset, prefix,suffix</font></center><br>
                    
                              """)
                    with gr.Row():
                      gr.Markdown("When activated, select what you want from the menus and press normal generate button, it also works with batch")
                    with gr.Row():
                      is_manual_enabled = grc.Checkbox(label="♻️Enable auto prompting", info="💬From dropdown selection", value=False)
                      is_manual_random = grc.Checkbox(label="🎲Enable random prompts", info="💬For each images in batch", value=False, interactive=True)
                    with gr.Row():
                      gr.Markdown("# ")
                    with gr.Row(): 
                      auto_final = grc.Textbox(label="Prompt preview:", elem_id="manual_prompt_result", show_label=True, lines=2, placeholder="The prompt that will be used", container=True)
                    with gr.Row():
                      gr.Markdown("# ")
                    with gr.Row():
                      for filename in os.listdir(folder_path):
                        if filename.endswith(".csv"):
                           file_path = os.path.join(folder_path, filename)
                           lines = []
                           with open(file_path, 'r', encoding='utf-8') as file:
                              lines = file.readlines()
                           lines = ["➡️" + line.strip() for line in lines]
                           lines.insert(0, "None\n")
                           lines.insert(1, "🎲Random\n")
                           dropdown_component = grc.Dropdown(label=f"{filename[3:-4]}", choices=lines, elem_id=f"{filename}_dropdown", container=True, value="None")
                           dropdowns.append(dropdown_component)
                    global dropdown_values
                    dropdown_values = [""] * len(dropdowns)                    
              with gr.Accordion("➡️Create prompt manually from categories", open=False):         
                     with gr.Column(scale=3):
                       #gr.Markdown("# Create prompt manually from categories")
                       gr.Markdown("💬Press the normal generate button to start generating image with the final prompt")
                       final = grc.Textbox(label="Final prompt which will be used to generate the image:", elem_id="creaprompt_prompt_final", show_label=True, lines=2, placeholder="The final prompt is displayed here", container=True)
                       Prefix = grc.Textbox(label="Prefix of the Prompt:", elem_id="prompt_prefix", show_label=True, lines=2, placeholder="Type your prefix or leave blank if you don't want it", container=True)
                       sufix = grc.Textbox(label="Suffix of the Prompt:", elem_id="prompt_sufix", show_label=True, lines=2, placeholder="Type your suffix or leave blank if you don't want it", container=True)
                       prompt = grc.Textbox(label="Created Prompt from categories:", elem_id="promptgen_prompt", show_label=True, lines=2, placeholder="Make the selection of your choice and Click Generate button", container=True)
                       gr.Markdown("# ")
                       checkbox_group_manu = grc.CheckboxGroup(label="Select Categories:", choices=checkboxes, default=['base'], min_width=50)
                       gr.Markdown("# ")
                       with gr.Row():
                            save_state_button_manu = gr.Button("Save your preset categories", elem_id="save_state_manu", variant="primary")
                            file_name_textbox_manu = grc.Textbox(elem_id="file_name_manu", show_label=False, placeholder="Enter your preset name", container=True)
                            file_dropdown_component_manu = gr.Dropdown(show_label=False, choices=get_config_files(), elem_id="file_dropdown_manu", value="Select a preset")
                       with gr.Row():
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
        
            is_enabled.select(fn=lambda x:gr.update(label = f"🎨CreaPrompt : {'Active' if x else 'Not Active'}"),inputs=is_enabled, outputs=[acc])
            is_collection_enabled.select(fn=lambda x:gr.update(label = f"🎨CreaPrompt : {'Active' if x else 'Not Active'}"),inputs=is_collection_enabled, outputs=[acc])
            is_manual_enabled.select(fn=lambda x:gr.update(label = f"🎨CreaPrompt : {'Active' if x else 'Not Active'}"),inputs=is_manual_enabled, outputs=[acc])
            save_state_button_manu.click(save_checkbox_state_manu, inputs= [checkbox_group_manu, file_name_textbox_manu], outputs=[file_dropdown_component_manu, file_dropdown_component])
            save_state_button.click(save_checkbox_state, inputs= [checkbox_group, file_name_textbox], outputs=[file_dropdown_component, file_dropdown_component_manu])                        
            file_dropdown_component.change(load_checkbox_state, inputs=[file_dropdown_component], outputs=[checkbox_group])
            file_dropdown_component_manu.change(load_checkbox_state, inputs=[file_dropdown_component_manu], outputs=[checkbox_group_manu])
            is_collection_enabled.select(uncheck_auto_box, inputs=[is_collection_enabled, is_enabled, is_manual_enabled], outputs=[is_enabled, is_manual_enabled])
            is_enabled.select(uncheck_auto_collection, inputs=[is_enabled, is_collection_enabled, is_manual_enabled], outputs=[is_collection_enabled, is_manual_enabled])
            is_manual_enabled.select(uncheck_auto_manual, inputs=[is_manual_enabled, is_enabled, is_collection_enabled], outputs=[is_collection_enabled, is_enabled])
            #is_enabled.select(active_random_prompt, inputs=[is_enabled, is_collection_enabled], outputs=[is_randomize])
            #is_collection_enabled.select(active_random_prompt, inputs=[is_enabled, is_collection_enabled], outputs=[is_randomize])
            for i, dropdown_component in enumerate(dropdowns):
                #dropdown_component.change(lambda selected_value, index=i: (handle_dropdown_change(selected_value, index), dropdown_change_handler(i)), inputs=[dropdown_component], outputs=[auto_final])
                dropdown_component.change(lambda selected_value, index=i: handle_dropdown_change(selected_value, index), inputs=[dropdown_component], outputs=[auto_final])
                   
                
     
            if is_img2img:
                
                submit.click(
                           fn=read_random_line_from_csv_files_auto,
                           inputs=checkbox_group_manu,
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
                           fn=read_random_line_from_csv_files_auto,
                           inputs=checkbox_group_manu,
                           outputs=prompt
                          )        
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[self.boxx])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[final])
                
        return [is_enabled, checkbox_group, is_randomize, is_collection_enabled, prefix_auto, sufix_auto, is_randomize_manu, is_manual_enabled, is_manual_random]
        
    def process(self, p, is_enabled, checkbox_group, is_randomize, is_collection_enabled, prefix_auto, sufix_auto, is_randomize_manu, is_manual_enabled, is_manual_random):
    
        batchCount = len(p.all_prompts)
        
        if is_manual_enabled:
           if(batchCount == 1):
              back_dropdown_values = dropdown_values.copy()
              concatenated_values = ""
              #print (dropdown_values)
              values_exist = False
              for i, value in enumerate(back_dropdown_values):
                 if value:
                    values_exist = True
                    if value[0] == "🎲":
                       back_dropdown_values[i] = read_random_line_from_csv_file_manual(i)
              if not values_exist:  
                 p.all_prompts[0] = "Please select categories"              
                 print("Please select categories")   
              else:                 
                 for value in back_dropdown_values:
                    if value:
                       concatenated_values += value + ","
                 concatenated_values = concatenated_values.rstrip(", ")
                 print("Prompt used for manual from categories:" + " " + concatenated_values)
                 p.extra_generation_params.update({"CreaPrompt":"manual from categories"})
                 p.all_prompts[0] = concatenated_values
           
           if(batchCount > 1):   
              for i, prompt in enumerate(p.all_prompts):
                  if(is_manual_random):
                     back_dropdown_values = dropdown_values.copy()
                     concatenated_values = ""
                     #print (dropdown_values)
                     values_exist = False
                     for a, value in enumerate(back_dropdown_values):
                        if value:
                           values_exist = True
                           if value[0] == "🎲":
                              back_dropdown_values[a] = read_random_line_from_csv_file_manual(a)
                     if not values_exist:  
                        p.all_prompts[i] = "Please select categories"  
                        if i == 0:                        
                           print("Please select categories")   
                     else:                 
                        for value in back_dropdown_values:
                           if value:
                              concatenated_values += value + ","
                        concatenated_values = concatenated_values.rstrip(", ")
                        print("Prompt used for manual from categories:" + " " + concatenated_values)
                        p.extra_generation_params.update({"CreaPrompt":"manual from categories"})
                        p.all_prompts[i] = concatenated_values
                  else:
                   if i == 0:
                     back_dropdown_values = dropdown_values.copy()
                     concatenated_values = ""
                     #print (dropdown_values)
                     values_exist = False
                     for a, value in enumerate(back_dropdown_values):
                        if value:
                           values_exist = True
                           if value[0] == "🎲":
                              back_dropdown_values[a] = read_random_line_from_csv_file_manual(a)
                     if not values_exist:  
                        concatenated_values = "Please select categories"
                        print("Please select categories")   
                     else:                 
                        for value in back_dropdown_values:
                           if value:
                              concatenated_values += value + ","
                        concatenated_values = concatenated_values.rstrip(", ")
                        print("Prompt used for manual from categories:" + " " + concatenated_values)
                   p.extra_generation_params.update({"CreaPrompt":"manual from categories"})
                   p.all_prompts[i] = concatenated_values 
    
        if is_collection_enabled:
           if(batchCount == 1):
              for i, prompt in enumerate(p.all_prompts):
                  randprompt=select_random_line_from_collection()  
              p.all_prompts[i] = randprompt
              print("Prompt used from collection:" + " " + randprompt)    
              p.extra_generation_params.update({"CreaPrompt":"Collection"})              

           if(batchCount > 1):
            randprompts = {}
            randprompt = ""
            for i, prompt in enumerate(p.all_prompts):
                if(is_randomize_manu):
                   randprompt = select_random_line_from_collection()
                   randprompts[i] = randprompt
                   p.all_prompts[i] = randprompts[i]
                   print("Prompt used from collection:" + " " + randprompts[i])
                else:
                    if i == 0:
                      randprompt = select_random_line_from_collection()
                      print("Prompt used from collection:" + " " + randprompt)
                p.all_prompts[i] = randprompt  
                p.extra_generation_params.update({"CreaPrompt":"Collection"})                
    
        if not is_enabled:
          # if is_manual and not is_collection_enabled:
           #   p.extra_generation_params.update({"CreaPrompt":"Manual mode"})
            #  print("passe")
           #print(is_manual)
           return

        if(batchCount == 1):
            for i, prompt in enumerate(p.all_prompts):
                randprompt= read_random_line_from_csv_files(checkbox_group)
                if prefix_auto:
                   randprompt = prefix_auto + "," + randprompt
                if sufix_auto:
                   randprompt = randprompt + "," + sufix_auto
            p.all_prompts[i] = randprompt
            print("Prompt used for random from categories:" + " " + randprompt)
            p.extra_generation_params.update({"CreaPrompt random From categories":", ".join([str(x) for x in checkbox_group])})
            
        if(batchCount > 1):
            randprompts = {}
            randprompt = ""
            for i, prompt in enumerate(p.all_prompts):
                if(is_randomize):
                   randprompt = read_random_line_from_csv_files(checkbox_group)
                   if prefix_auto:
                      randprompt = prefix_auto + "," + randprompt
                   if sufix_auto:
                      randprompt = randprompt + "," + sufix_auto
                   randprompts[i] = randprompt
                   p.all_prompts[i] = randprompts[i]
                   print("Prompt used for random from categories:" + " " + randprompts[i])
                else:
                    if i == 0:
                      randprompt = read_random_line_from_csv_files(checkbox_group)
                      if prefix_auto:
                         randprompt = prefix_auto + "," + randprompt
                      if sufix_auto:
                         randprompt = randprompt + "," + sufix_auto
                      print("Prompt used for random from categories:" + " " + randprompt)
                p.all_prompts[i] = randprompt
                p.extra_generation_params.update({"CreaPrompt random From categories":", ".join([str(x) for x in checkbox_group])})

        

    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component









