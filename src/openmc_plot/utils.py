import streamlit as st
import openmc

def make_pretend_mats(set_mat_ids):
    
    my_mats = openmc.Materials()
    for mat_id in set_mat_ids:
        new_mat = openmc.Material()
        new_mat.id = mat_id
        new_mat.add_nuclide("He4", 1)
        # adds a single nuclide that is in minimal cross section xml to avoid material failing
        my_mats.append(new_mat)
    return my_mats

def save_uploadedfile(uploadedfile):
    with open(uploadedfile.name, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success(f"Saved File to {uploadedfile.name}")
