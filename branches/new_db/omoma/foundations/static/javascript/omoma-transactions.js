function updatetransactions(data) {
        $('div#transactions table').html(transactionsinittemplate(data));
}

function inittransactionsdisplay() {
    var rowdirective = {
        '@id':'transaction#{id}',
        'span.description':'description',
        'span.originaldescription':function(arg) { desc = arg.context.original_description; return desc?' ('+desc+')':''; },
        'span.amount': {
            'amount<-amounts': {
                'span.amountvalue':'amount.value',
                //~ 'span.amountaccount':' (#{amount.account})',
                'span.amountaccount':function(arg) { account = arg.item.account; return account?' ('+account+')':''; },
            }
        }
    }
    transactionsrowtemplate = $('div#transactions tr').compile(rowdirective);

    var initdirective = {
        'tr': {
            'transaction<-context': {
                '.': function(context) { return transactionsrowtemplate(context.transaction.item) }
            }
        }
    }
    transactionsinittemplate = $('div#transactions table').compile(initdirective);

    // Apply transactions filter once and prepare interactive usage
    $('form#transactionsfilter').ajaxSubmit(function(response) { updatetransactions(response); });
    $('form#transactionsfilter').ajaxForm(function(response) { updatetransactions(response); });
}
