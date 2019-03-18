import _ from 'lodash';

export default {
    getTranslated(i18n_field, language, fallback_languages) {
        if(language === undefined) {
            language = 'en'
        }
        if(fallback_languages === undefined) {
            fallback_languages = {};
        }

        let translated_value = i18n_field[language];
        if(translated_value !== undefined) {
          return translated_value;  // localized value is available for the current language
        }

        // localized value is missing, search for fallback translation values
        _.forOwn(fallback_languages, (language_list, target_language) => {
          if(_.includes(language_list, language)) {
              translated_value = i18n_field[target_language];
              return false;
          }
        });
        return translated_value || '--';
    },
};
