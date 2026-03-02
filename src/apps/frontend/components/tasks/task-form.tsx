import { useFormik } from 'formik';
import React from 'react';
import * as Yup from 'yup';
import { ButtonType, ButtonKind } from 'frontend/types/button';

import { Button, FormControl, Input, VerticalStackLayout, HorizontalStackLayout } from 'frontend/components';

interface TaskFormProps {
    initialValues?: {
        title: string;
        description: string;
    };
    onSubmit: (values: { title: string; description: string }) => Promise<void>;
    onCancel: () => void;
    submitLabel?: string;
}

const TaskForm: React.FC<TaskFormProps> = ({
    initialValues = { title: '', description: '' },
    onSubmit,
    onCancel,
    submitLabel = 'Save',
}) => {
    const formik = useFormik({
        initialValues,
        validationSchema: Yup.object({
            title: Yup.string().required('Title is required'),
            description: Yup.string().required('Description is required'),
        }),
        onSubmit: async (values, { setSubmitting }) => {
            await onSubmit(values);
            setSubmitting(false);
        },
    });

    return (
        <form onSubmit={formik.handleSubmit} className="w-full">
            <VerticalStackLayout gap={4}>
                <FormControl label="Title" error={formik.touched.title ? formik.errors.title : undefined}>
                    <Input
                        name="title"
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.title}
                        placeholder="Task Title"
                        error={formik.touched.title ? formik.errors.title : undefined}
                    />
                </FormControl>

                <FormControl
                    label="Description"
                    error={formik.touched.description ? formik.errors.description : undefined}
                >
                    <div className={`w-full rounded-lg border bg-white p-4 outline-none focus-within:border-primary ${formik.touched.description && formik.errors.description ? 'border-red-500' : 'border-stroke'
                        }`}>
                        <textarea
                            name="description"
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            value={formik.values.description}
                            placeholder="Task Description"
                            className="w-full h-24 resize-none outline-none"
                        />
                    </div>
                </FormControl>

                <HorizontalStackLayout gap={3}>
                    <Button type={ButtonType.SUBMIT} isLoading={formik.isSubmitting}>
                        {submitLabel}
                    </Button>
                    <Button type={ButtonType.BUTTON} kind={ButtonKind.SECONDARY} onClick={onCancel} disabled={formik.isSubmitting}>
                        Cancel
                    </Button>
                </HorizontalStackLayout>
            </VerticalStackLayout>
        </form>
    );
};

export default TaskForm;
