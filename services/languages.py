

def load_languages(errors):
    if len(st.session_state['locations']) < 1:
        errors['languages'] = 'You need to select the locations before we can suggest you the languages'
    with st.spinner('Loading'):
        messages=[
            {
                "role": "system",
                "content": "Your task is to list down all the major languages spoken in the given locations in the last 80 years. \n\n[step 1]\nFor each location include the top 5 local, regional, national, and international languages popularly spoken in the given locations.\n\n[step 2]\nInclude the estimated percentage of people who may speak the given language in the given locations. Do it for each of the locations.\n\n[Step 3]\nReturn the response in the following JSON format:\n\n[ \n  {\n    language: language_name, \n    population: 10%,\n    location: location_name\n  }\n ]\n\nPlease ensure that the response is strictly in the format shared above"
            },
            {
                "role": "user",
                "content": "Locations: " + ', '.join(st.session_state['locations'])
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            temperature = 0,
            max_tokens = 512,
            top_p = 1,
            frequency_penalty = 0,
            presence_penalty = 0
        )
        try:
            original_list = json.loads(response.choices[0].message.content)
            st.session_state['languages'] = sort_languages(original_list)
            if 'languages' in errors:
                del(errors['languages'])
        except Exception as err:
            st.write(err)

def sort_languages(languages):
    languages.sort(key=lambda x: x['population'], reverse=True)
    _result = []
    for language in languages:
        if language.get('language') not in _result:
            _result.append(language.get('language'))
    return _result
