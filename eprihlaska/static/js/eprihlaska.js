function install_form_change_trigger() {
  /* Mark the form as changed */
  $("form :input").not('.chosen-search-input').change(function() {
    $(this).closest('form').data('changed_unconfirmed', true);
  });

  /* Clean the mark on submit */
  $("form").submit(function(){
    $(this).data('changed_unconfirmed', false);
  });

  /* Trigger a (most probably generic) message if the form is marked */
  $(window).on('beforeunload', function(){
    if ($('form').data('changed_unconfirmed')) {
      return "Chystáte sa opustiť stránku bez uloženia zmien.";
    }
  });
}

