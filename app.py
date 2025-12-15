# streamlit_app.py - Streamlit HR Chatbot
import streamlit as st
from hr_app.agent import chat_with_hr

def main():
    st.set_page_config(page_title="HR Chatbot", page_icon="🤖", layout="wide")
    
    st.title(" HR Management Chatbot")
    st.markdown("Chat with me to manage employees! I can add, view, search, update, and delete employee records.")
    
    # Examples to help users get started
    with st.expander("💡 Example commands you can try", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Add Employee:**
            - "Add John Doe with ID JD001 in Engineering as Developer salary 75000"
            - "Create new employee Sarah Smith ID SS202 Marketing Manager $85000"
            
            **View Employees:**
            - "Show all employees"
            - "List employees"
            """)
        with col2:
            st.markdown("""
            **Search:**
            - "Find employee with ID JD001"
            - "Search for employees named John"
            
            **Update/Delete:**
            - "Update JD001 salary to 80000"
            - "Delete employee SS202"
            """)
    
    # Initialize chat history
    if "hr_chat_history" not in st.session_state:
        st.session_state.hr_chat_history = []
    
    # Display chat messages from history
    for message in st.session_state.hr_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What HR action would you like to perform?"):
        # Add user message to chat history
        st.session_state.hr_chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Processing your request..."):
                # Get response from the HR agent
                response = chat_with_hr(prompt)
                message_placeholder.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.hr_chat_history.append({"role": "assistant", "content": response})
        
        # Add clear chat button
        if st.button("Clear Chat"):
            st.session_state.hr_chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()