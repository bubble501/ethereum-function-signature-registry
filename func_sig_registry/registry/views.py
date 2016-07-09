from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import (
    ListView,
    TemplateView,
)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from django_tables2 import SingleTableView

from func_sig_registry.utils.encoding import (
    decode_hex,
    force_text,
)

from .models import Signature
from .tables import SignatureTable
from .forms import (
    SignatureForm,
    SolidityImportForm,
    SignatureSearchForm,
)


class SiteIndexView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(SiteIndexView, self).get_context_data(**kwargs)
        context['serializer'] = SignatureSearchForm()
        context['total_signatures'] = Signature.objects.count()
        return context


class SignatureListView(SingleTableView, ListView):
    model = Signature
    table_class = SignatureTable
    table_pagination = {
        'per_page': 10
    }

    def get_queryset(self):
        queryset = super(SignatureListView, self).get_queryset()
        if self.request.GET.get('bytes4_signature'):
            hex_signature = self.request.GET['bytes4_signature']
            bytes4_signature = force_text(decode_hex(hex_signature))
            return queryset.filter(bytes_signature__bytes4_signature=bytes4_signature)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SignatureListView, self).get_context_data(**kwargs)
        if self.request.GET.get('bytes4_signature'):
            serializer = SignatureSearchForm(data=self.request.GET)
            serializer.is_valid()
        else:
            serializer = SignatureSearchForm()
        context['serializer'] = serializer
        return context


class SignatureCreateView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registry/signature_create.html'
    serializer_class = SignatureForm

    def get(self, *args, **kwargs):
        serializer = self.get_serializer()
        return Response({
            'serializer': serializer,
        })

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        signature = serializer.save()
        messages.success(
            self.request._request,
            "Added signature '{0}' for function '{1}'".format(
                signature.bytes_signature.get_hex_display(),
                signature.text_signature,
            ),
        )
        return redirect('signature-list')


class SolidityImportView(generics.GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registry/solidity_source_import.html'
    serializer_class = SolidityImportForm

    def get(self, *args, **kwargs):
        serializer = self.get_serializer()
        return Response({
            'serializer': serializer,
        })

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        results = serializer.save()
        import_results = []
        for file_obj in results['source_files']:
            import_results.extend(Signature.import_from_solidity_source(file_obj))
        num_processed = len(import_results)
        num_imported = sum(tuple(zip(*import_results))[1])
        num_duplicates = num_processed - num_imported
        messages.success(
            self.request._request,
            "Found {0} function signatures.  Imported {1}, Skipped {2} duplicates.".format(
                num_processed, num_imported, num_duplicates,
            ),
        )
        return redirect('signature-list')